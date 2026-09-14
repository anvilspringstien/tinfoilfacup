#!/usr/bin/env python3
"""Build a production-candidate Clubfinder cleanup on a non-main branch.

Migrates sourced Extra Preliminary outcomes into competition.result_history,
then blanks the two regression-proven legacy lookup tables:
- PRELIM_FIXTURES_BY_CLUB
- EPR_RESULTS_BY_TIE

The caller supplies the review/audit candidate JSON. This script does not fetch
network resources and does not touch main by itself.
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / "competition.json"
HTML = ROOT / "clubfinder.html"
REPORT = ROOT / "legacy-table-cleanup-candidate.md"

if len(sys.argv) != 2:
    raise SystemExit("usage: build_legacy_table_cleanup_candidate.py <epr-canonical-candidate.json>")
CAND = Path(sys.argv[1])


def clean_team_name(value):
    s = str(value or "").strip()
    # Football Web Pages display can include score annotations attached to names.
    s = re.sub(r"\(\d+\)", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def short_name(value):
    s = clean_team_name(value)
    return re.sub(r"\s+(FC|AFC|CFC)$", "", s, flags=re.I).strip()


def semantic_key(r):
    return (
        str(r.get("round") or ""),
        str(r.get("date") or ""),
        short_name(r.get("home")).lower(),
        short_name(r.get("away")).lower(),
        r.get("home_score"),
        r.get("away_score"),
        str(r.get("decision") or "").lower(),
        short_name(r.get("winner")).lower(),
    )


ALIASES = {
    "Newton Aycliffe": ["Newton Aycliffe FC"],
    "Kendal Town": ["Kendal Town FC"],
    "Marske United": ["Marske United FC"],
    "Abbey Hulton United": ["Abbey Hulton United FC"],
    "Kidsgrove Athletic": ["Kidsgrove Athletic FC"],
    "Boro Rangers": ["Boro Rangers FC"],
    "AFC Varndenians": ["AFC Varndeanians", "AFC Varndeanians FC"],
    "Atherton Laburnum Rovers": ["Atherton LR"],
    "Eastwood CFC": ["Eastwood Community", "Eastwood Community FC"],
    "Irlam Town": ["Irlam", "Irlam FC"],
    "Royal Wootton Bassett": ["Royal Wootton Bassett Town", "Royal Wootton Bassett Town FC"],
    "Sherbourne Town": ["Sherborne Town", "Sherborne Town FC"],
    "Bournemouth FC": ["Bournemouth Poppies", "Bournemouth Poppies FC"],
    "Bedfont Sports": ["Bedfont Sports Club", "Bedfont Sports Club FC"],
}


def keys_for_team(name):
    canonical = clean_team_name(name)
    vals = [canonical, short_name(canonical)]
    vals += ALIASES.get(canonical, [])
    vals += ALIASES.get(short_name(canonical), [])
    out = []
    for value in vals:
        value = str(value).strip()
        if value and value not in out:
            out.append(value)
    return out


def blank_object_assignment(text, name):
    m = re.search(r"\bconst\s+" + re.escape(name) + r"\s*=\s*\{", text)
    if not m:
        raise SystemExit(f"ABORT: {name} assignment not found")
    start = m.end() - 1
    depth = 0
    quote = None
    esc = False
    end = None
    for i in range(start, len(text)):
        ch = text[i]
        if quote:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == quote:
                quote = None
        else:
            if ch in "'\"`":
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
    if end is None:
        raise SystemExit(f"ABORT: {name} object not balanced")
    removed = end - start - 2
    return text[:start] + "{}" + text[end:], removed


data = json.loads(COMP.read_text(encoding="utf-8"))
cand = json.loads(CAND.read_text(encoding="utf-8"))
rows = cand.get("candidate_rows") or []
excluded = cand.get("excluded_rows") or []
if len(rows) != 218 or excluded:
    raise SystemExit(f"ABORT: expected 218 sourced EPR rows and 0 unresolved; got {len(rows)} / {len(excluded)}")

rh = data.setdefault("result_history", {})
original_keys = len(rh)
created_keys = 0
appended = 0

for src in rows:
    r = {k: src.get(k) for k in (
        "round", "date", "home", "away", "home_score", "away_score",
        "winner", "status", "decision", "source_url"
    )}
    r["home"] = clean_team_name(r.get("home"))
    r["away"] = clean_team_name(r.get("away"))
    r["winner"] = clean_team_name(r.get("winner"))
    if str(r.get("decision") or "").lower() == "walkover":
        r["home_score"] = None
        r["away_score"] = None
    for team in (r.get("home"), r.get("away")):
        for key in keys_for_team(team):
            arr = rh.get(key)
            if arr is None:
                arr = []
                rh[key] = arr
                created_keys += 1
            if not isinstance(arr, list):
                raise SystemExit(f"ABORT: result_history[{key!r}] is not a list")
            sk = semantic_key(r)
            if not any(semantic_key(x) == sk for x in arr if isinstance(x, dict)):
                arr.append(dict(r))
                arr.sort(key=lambda x: (str(x.get("date") or ""), str(x.get("round") or "")))
                appended += 1

COMP.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

text = HTML.read_text(encoding="utf-8")
text, prelim_removed = blank_object_assignment(text, "PRELIM_FIXTURES_BY_CLUB")
text, epr_removed = blank_object_assignment(text, "EPR_RESULTS_BY_TIE")
HTML.write_text(text, encoding="utf-8")

new = json.loads(COMP.read_text(encoding="utf-8"))["result_history"]

def has_result(team, home, away, hs, as_):
    return any(
        short_name(x.get("home")).lower() == short_name(home).lower()
        and short_name(x.get("away")).lower() == short_name(away).lower()
        and x.get("home_score") == hs
        and x.get("away_score") == as_
        for x in new.get(team, []) if isinstance(x, dict)
    )

checks = {
    "Newton Aycliffe canonical EPR": has_result("Newton Aycliffe FC", "Newton Aycliffe", "Kendal Town", 0, 1),
    "Marske administrative bye": any(
        str(x.get("decision") or "").lower() == "walkover"
        and short_name(x.get("winner")).lower() == "marske united"
        for x in new.get("Marske United FC", []) if isinstance(x, dict)
    ),
    "Abbey Hulton administrative award": any(
        str(x.get("decision") or "").lower() == "walkover"
        and short_name(x.get("winner")).lower() == "abbey hulton united"
        for x in new.get("Abbey Hulton United FC", []) if isinstance(x, dict)
    ),
}
for label, ok in checks.items():
    if not ok:
        raise SystemExit("ABORT: " + label + " missing after canonical migration")

REPORT.write_text("\n".join([
    "# Legacy table cleanup production candidate",
    "",
    "Built on a non-main candidate branch. Production main unchanged.",
    "",
    f"- Sourced Extra Preliminary rows migrated: **{len(rows)}**",
    f"- Existing result_history keys before migration: **{original_keys}**",
    f"- New result_history keys created: **{created_keys}**",
    f"- History records appended across lookup aliases: **{appended}**",
    f"- PRELIM_FIXTURES_BY_CLUB payload removed: **{prelim_removed} bytes**",
    f"- EPR_RESULTS_BY_TIE payload removed: **{epr_removed} bytes**",
    f"- Combined legacy payload removed: **{prelim_removed + epr_removed} bytes**",
    "",
    "Canonical proof points:",
    "",
    *[f"- {label}: **PASS**" for label, ok in checks.items() if ok],
    "",
]) + "\n", encoding="utf-8")

print("LEGACY TABLE CLEANUP CANDIDATE: PREPARED")
print("candidate EPR rows:", len(rows))
print("new result_history keys:", created_keys)
print("history records appended:", appended)
print("PRELIM bytes removed:", prelim_removed)
print("EPR bytes removed:", epr_removed)
print("combined bytes removed:", prelim_removed + epr_removed)
print("Production main untouched.")
