#!/usr/bin/env python3
"""Guarded automatic Emirates FA Cup draw detector/importer.

The official Emirates FA Cup fixtures endpoint (competitionId=1) is authoritative
for fixture publication detection. Only the round immediately after
competition.json/source_round can be promoted.

Existing result/custody history is never rewritten; the outgoing active fixture
map is archived in round_fixtures before the new round becomes active.
"""
import argparse
import html as H
import json
import re
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
REPORT = ROOT / "updater/draw-watch-report.json"
# IMPORTANT: competitionId=1 is the Emirates FA Cup. Do not substitute another
# FA competition ID (for example the FA Trophy) into this production watcher.
FA_PAGE = "https://www.thefa.com/Competitions/Fixtures/Fixtures?competitionId=1&page={}"
OFFICIAL_SOURCE = "https://www.thefa.com/competitions/thefacup/fixtures"
UA = {"User-Agent": "Mozilla/5.0 TinFoilFACupDrawWatcher/1.1", "Accept": "text/html,application/xhtml+xml"}

ROUND_ORDER = [
    "Extra Preliminary Round",
    "Preliminary Round",
    "First Round Qualifying",
    "Second Round Qualifying",
    "Third Round Qualifying",
    "Fourth Round Qualifying",
    "First Round Proper",
    "Second Round Proper",
    "Third Round Proper",
    "Fourth Round Proper",
    "Fifth Round Proper",
    "Quarter Final",
    "Semi Final",
    "Final",
]
ROUND_ALIASES = {
    "Extra Preliminary Round": ["Extra Preliminary Round"],
    "Preliminary Round": ["Preliminary Round"],
    "First Round Qualifying": ["First Round Qualifying", "First Qualifying Round"],
    "Second Round Qualifying": ["Second Round Qualifying", "Second Qualifying Round"],
    "Third Round Qualifying": ["Third Round Qualifying", "Third Qualifying Round"],
    "Fourth Round Qualifying": ["Fourth Round Qualifying", "Fourth Qualifying Round"],
    "First Round Proper": ["First Round Proper", "First Round"],
    "Second Round Proper": ["Second Round Proper", "Second Round"],
    "Third Round Proper": ["Third Round Proper", "Third Round"],
    "Fourth Round Proper": ["Fourth Round Proper", "Fourth Round"],
    "Fifth Round Proper": ["Fifth Round Proper", "Fifth Round"],
    "Quarter Final": ["Quarter Final", "Quarter-Final", "Quarter Finals", "Quarter-Finals"],
    "Semi Final": ["Semi Final", "Semi-Final", "Semi Finals", "Semi-Finals"],
    "Final": ["Final"],
}
_ALIAS_TO_ROUND = {}
for _canonical, _aliases in ROUND_ALIASES.items():
    for _alias in _aliases:
        _ALIAS_TO_ROUND[_alias.lower()] = _canonical
# Longest-first alternatives prevent "Final" from matching inside "Semi Final"
# and "First Round" from matching inside "First Round Qualifying".
ROUND_RE = re.compile(
    r"(?<!\w)(" + "|".join(re.escape(a) for a in sorted(_ALIAS_TO_ROUND, key=len, reverse=True)) + r")(?!\w)",
    re.I,
)
DATE_RE = re.compile(r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})\b", re.I)


def clean(x):
    x = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", x, flags=re.I | re.S)
    return " ".join(H.unescape(re.sub(r"<[^>]+>", " ", x)).replace("\xa0", " ").split())


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"\b(fc|afc|cfc)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def canonical_conditional(s):
    s = " ".join((s or "").split())
    if " / " in s:
        parts = [p.strip() for p in s.split(" / ") if p.strip()]
        if len(parts) > 1:
            return " or ".join(parts)
    return s


def alternatives(s):
    return [p.strip() for p in re.split(r"\s+or\s+", s or "", flags=re.I) if p.strip()]


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=35) as r:
        return r.read().decode("utf-8", "replace")


def round_from_context(context):
    matches = list(ROUND_RE.finditer(clean(context)))
    if not matches:
        return ""
    return _ALIAS_TO_ROUND[matches[-1].group(1).lower()]


def date_from_context(context):
    text = clean(context)
    matches = list(DATE_RE.finditer(text))
    if not matches:
        return ""
    m = matches[-1]
    try:
        return datetime.strptime(f"{m.group(2)} {m.group(3)} {m.group(4)}", "%d %B %Y").date().isoformat()
    except ValueError:
        return ""


def parse_page(page_html):
    rows = []
    for m in re.finditer(r"<tr\b[^>]*>.*?</tr>", page_html, re.I | re.S):
        row = m.group(0)
        cells = [clean(x) for x in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row, re.I | re.S)]
        if not cells:
            continue
        try:
            vi = next(i for i, c in enumerate(cells) if c.upper() in {"VS", "V", "V."})
        except StopIteration:
            continue
        if vi < 1 or vi + 1 >= len(cells):
            continue
        context = page_html[max(0, m.start() - 18000):m.start()]
        rnd = round_from_context(context)
        date = date_from_context(context)
        home = canonical_conditional(cells[vi - 1])
        away = canonical_conditional(cells[vi + 1])
        kickoff = next((c for c in cells[:vi] if re.fullmatch(r"\d{1,2}:\d{2}", c)), "15:00")
        if rnd and home and away:
            rows.append({"round": rnd, "home": home, "away": away, "date": date, "kickoff": kickoff})
    return rows


def unique_ties(rows):
    out = {}
    for r in rows:
        k = (r["round"], norm(r["home"]), norm(r["away"]), r.get("date", ""))
        out[k] = r
    return list(out.values())


def fixture_values(fixtures):
    vals = fixtures.values() if isinstance(fixtures, dict) else fixtures or []
    out, seen = [], set()
    for f in vals:
        if not isinstance(f, dict) or not f.get("home") or not f.get("away"):
            continue
        k = (norm(f["home"]), norm(f["away"]), f.get("date", ""))
        if k not in seen:
            seen.add(k)
            out.append(dict(f))
    return out


def validate_target(target, ties):
    if len(ties) < 20 and target not in {"Quarter Final", "Semi Final", "Final"}:
        raise SystemExit(f"Publication blocked: only {len(ties)} {target} ties found on official Emirates FA Cup fixture pages.")
    if target == "Quarter Final" and len(ties) != 4:
        raise SystemExit(f"Publication blocked: expected 4 Quarter Final ties, found {len(ties)}.")
    if target == "Semi Final" and len(ties) != 2:
        raise SystemExit(f"Publication blocked: expected 2 Semi Final ties, found {len(ties)}.")
    if target == "Final" and len(ties) != 1:
        raise SystemExit(f"Publication blocked: expected 1 Final tie, found {len(ties)}.")

    concrete = []
    for f in ties:
        for side in (f["home"], f["away"]):
            if " or " not in side.lower():
                concrete.append(norm(side))
    dupes = sorted(k for k, n in Counter(concrete).items() if k and n > 1)
    if dupes:
        raise SystemExit("Publication blocked: concrete clubs appear in more than one target-round tie: " + str(dupes[:12]))

    if not any(f.get("date") for f in ties):
        raise SystemExit("Publication blocked: official target-round rows had no parseable fixture dates.")


def fixture_map(ties):
    out = {}
    suffix = re.compile(r"\s+(FC|AFC|CFC)$", re.I)
    for f in ties:
        rec = dict(f)
        if " or " in rec["home"].lower() or " or " in rec["away"].lower():
            rec["conditional"] = True
        for club in alternatives(rec["home"]) + alternatives(rec["away"]):
            out[club] = rec
            out.setdefault(suffix.sub("", club), rec)
    return out


def write_report(**fields):
    base = {"checked_at": datetime.now(timezone.utc).isoformat(), "official_source": OFFICIAL_SOURCE, "competition_id": 1}
    base.update(fields)
    REPORT.write_text(json.dumps(base, indent=2) + "\n")
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--max-pages", type=int, default=40)
    args = ap.parse_args()

    data = json.loads(DATA.read_text())
    current = data.get("source_round", "")
    if current not in ROUND_ORDER:
        write_report(status="blocked", error=f"Unknown canonical source_round: {current!r}")
        raise SystemExit(f"Draw watcher cannot determine current canonical round from source_round={current!r}.")
    idx = ROUND_ORDER.index(current)
    if idx + 1 >= len(ROUND_ORDER):
        write_report(status="complete", current_round=current, target_round=None, target_ties_detected=0, published=False)
        print("No later Emirates FA Cup round exists after", current)
        return
    target = ROUND_ORDER[idx + 1]

    all_rows = []
    pages_checked = 0
    fetch_stop = "max-pages"
    for page in range(1, args.max_pages + 1):
        try:
            page_html = fetch(FA_PAGE.format(page))
        except urllib.error.HTTPError as e:
            # The FA endpoint returns an error after its last pagination page.
            # That marks the end of the current fixture catalogue, not a failed scan.
            if page > 1 and e.code in {400, 404, 500}:
                fetch_stop = f"end-of-pagination-http-{e.code}"
                break
            write_report(status="error", current_round=current, target_round=target, pages_checked=pages_checked, error=f"HTTP {e.code} on page {page}")
            raise
        except urllib.error.URLError as e:
            write_report(status="error", current_round=current, target_round=target, pages_checked=pages_checked, error=f"URL error on page {page}: {e.reason}")
            raise

        pages_checked += 1
        rows = parse_page(page_html)
        all_rows.extend(rows)
        if not rows and page > 5:
            fetch_stop = "empty-page"
            break

    target_ties = unique_ties([r for r in all_rows if r["round"] == target])
    report = write_report(
        status="detected" if target_ties else "no-new-draw",
        current_round=current,
        target_round=target,
        target_ties_detected=len(target_ties),
        pages_checked=pages_checked,
        pagination_stop=fetch_stop,
        published=False,
    )

    if not target_ties:
        print(f"NO NEW DRAW: official Emirates FA Cup fixture pages do not yet expose {target}.")
        return

    validate_target(target, target_ties)
    print(f"OFFICIAL EMIRATES FA CUP DRAW DETECTED: {target}: {len(target_ties)} ties")
    if not args.publish:
        print("DRY RUN: competition.json unchanged.")
        return

    old = fixture_values(data.get("fixtures") or {})
    archive = data.setdefault("round_fixtures", {})
    if old and current not in archive:
        archive[current] = old

    data["fixtures"] = fixture_map(target_ties)
    data["source_round"] = target
    data["source_tie_count"] = len(target_ties)
    data["source_url"] = OFFICIAL_SOURCE
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    report.update({
        "status": "published",
        "published": True,
        "archived_outgoing_round": current,
        "archived_outgoing_ties": len(old),
    })
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"PUBLISHED: {target}: {len(target_ties)} ties; preserved {len(old)} outgoing ties in round_fixtures/{current}.")


if __name__ == "__main__":
    main()
