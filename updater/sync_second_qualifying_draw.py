#!/usr/bin/env python3
"""Guarded importer for the Emirates FA Cup Second Round Qualifying draw.

Source of truth: The FA's Emirates FA Cup fixtures page only.

Behaviour:
- If The FA has not yet published any Second Round Qualifying rows, exit cleanly.
- If a partial draw is visible, abort without writing.
- Require exactly 80 Second Round Qualifying ties.
- Validate all 112 First Qualifying progression slots: each confirmed winner must
  appear exactly once, and each unresolved First Qualifying tie must be represented
  by one conditional side containing both clubs.
- Require exactly 48 genuine new entrants at this stage.
- Reject eliminated First Qualifying clubs appearing as resolved entrants.
- Merge the validated draw into competition.json without removing First Qualifying
  chronology or results.
"""

from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "competition.json"
FA_FIXTURES_URL = "https://www.thefa.com/competitions/thefacup/fixtures"
ROUND = "Second Round Qualifying"
ROUND_DATE = "2026-09-19"
EXPECTED_TIES = 80
EXPECTED_NEW_ENTRANTS = 48
UA = "Mozilla/5.0 TinFoilFACupSecondQualifyingDraw/7.9.24"


def fetch(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"},
    )
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def clean(x: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", x)).replace("\xa0", " ").split())


def norm(s: str) -> str:
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"\b(association football club|football club)\b", " ", s)
    s = re.sub(r"\b(fc|afc|cfc)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def aliases(name: str) -> set[str]:
    if not name:
        return set()
    suffix = re.compile(r"\s+(FC|AFC|CFC)$", re.I)
    out = {name, suffix.sub("", name)}
    if not suffix.search(name):
        out |= {name + " FC", name + " AFC"}
    return {x for x in out if x}


def cells(row: str) -> list[str]:
    return [clean(x) for x in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row, re.I | re.S)]


def parse_fa_second_qualifying(html: str) -> list[dict]:
    """Parse only rows belonging to the Emirates FA Cup Second Round Qualifying."""
    fixtures = []
    current_round = ""
    current_date = ""

    for row in re.findall(r"<tr\b[^>]*>.*?</tr>", html, re.I | re.S):
        c = [x for x in cells(row) if x]
        if not c:
            continue
        joined = " ".join(c)

        if ROUND.lower() in joined.lower():
            current_round = ROUND
            dm = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(20\d{2})", joined)
            if dm:
                try:
                    current_date = datetime.strptime(
                        f"{dm.group(1)} {dm.group(2)} {dm.group(3)}", "%d %B %Y"
                    ).date().isoformat()
                except ValueError:
                    pass
            continue

        # A new round heading ends our section.
        if "Qualifying" in joined and ROUND.lower() not in joined.lower() and len(c) <= 3:
            current_round = ""
            continue

        if current_round != ROUND:
            continue

        # Typical FA fixture row: kick-off, tie no., home, VS, away, ...
        try:
            vi = next(i for i, x in enumerate(c) if x.strip().lower() in {"v", "vs"})
        except StopIteration:
            vi = -1
        if vi < 1 or vi + 1 >= len(c):
            continue

        home = c[vi - 1].strip()
        away = c[vi + 1].strip()
        if not home or not away:
            continue

        kickoff = "15:00"
        for x in c[:vi]:
            if re.fullmatch(r"\d{1,2}:\d{2}", x):
                kickoff = x
                break

        number = None
        for x in c[:vi]:
            if re.fullmatch(r"\d{1,3}", x):
                number = int(x)

        fixtures.append(
            {
                "round": ROUND,
                "home": home,
                "away": away,
                "date": current_date or ROUND_DATE,
                "kickoff": kickoff,
                "number": number,
                "source_url": FA_FIXTURES_URL,
            }
        )

    uniq = {}
    for f in fixtures:
        key = (norm(f["home"]), norm(f["away"]))
        if key in uniq:
            raise SystemExit(f"ABORT: duplicate Second Qualifying tie: {f['home']} v {f['away']}")
        uniq[key] = f
    return list(uniq.values())


def canonical_first_qualifying(data: dict) -> list[dict]:
    out = []
    seen = set()
    for f in (data.get("fixtures") or {}).values():
        if not isinstance(f, dict) or f.get("round") != "First Round Qualifying":
            continue
        if not f.get("home") or not f.get("away"):
            continue
        key = (norm(f["home"]), norm(f["away"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(f))
    return out


def latest_first_qualifying_result(data: dict, fixture: dict) -> dict | None:
    candidates = []
    for arr in (data.get("result_history") or {}).values():
        if not isinstance(arr, list):
            continue
        for r in arr:
            if not isinstance(r, dict) or r.get("round") != "First Round Qualifying":
                continue
            if norm(r.get("home")) == norm(fixture["home"]) and norm(r.get("away")) == norm(fixture["away"]):
                candidates.append(r)
    if not candidates:
        return None
    # Duplicate aliases may surface the same semantic result; newest date is sufficient here.
    candidates.sort(key=lambda r: r.get("date", ""))
    return candidates[-1]


def decisive_winner(r: dict | None) -> str:
    if not r:
        return ""
    try:
        hs, as_ = int(r.get("home_score")), int(r.get("away_score"))
    except (TypeError, ValueError):
        return r.get("winner") or ""
    if hs > as_:
        return r.get("home") or ""
    if as_ > hs:
        return r.get("away") or ""
    return r.get("winner") or "" if r.get("decision") == "penalties" else ""


def side_contains_both(side: str, a: str, b: str) -> bool:
    ns = " " + norm(side) + " "
    na, nb = norm(a), norm(b)
    return bool(na and nb and na in ns and nb in ns)


def fixture_sides(fixtures: list[dict]) -> list[str]:
    out = []
    for f in fixtures:
        out.extend([f["home"], f["away"]])
    return out


def add_fixture_mapping(mapping: dict, fixture: dict) -> None:
    """Map resolved clubs and 'X or Y' conditional sides to the same next fixture."""
    for side in (fixture["home"], fixture["away"]):
        names = {side}
        # The FA commonly renders unresolved replay slots as 'Club A or Club B'.
        parts = re.split(r"\s+or\s+", side, flags=re.I)
        if len(parts) == 2:
            names |= {p.strip() for p in parts if p.strip()}
        for name in names:
            for alias in aliases(name):
                mapping[alias] = fixture


data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
first = canonical_first_qualifying(data)
if len(first) != 112:
    raise SystemExit(f"ABORT: expected 112 canonical First Qualifying ties, got {len(first)}")

html = fetch(FA_FIXTURES_URL)
draw = parse_fa_second_qualifying(html)

if not draw:
    print("SECOND QUALIFYING DRAW: not yet published on Emirates FA Cup fixtures page")
    print("Competition data: UNCHANGED")
    raise SystemExit(0)
if len(draw) != EXPECTED_TIES:
    raise SystemExit(f"ABORT: partial/invalid Second Qualifying draw: expected {EXPECTED_TIES} ties, got {len(draw)}")

sides = fixture_sides(draw)
side_norms = [norm(x) for x in sides]
if len(side_norms) != 160 or len(set(side_norms)) != 160:
    raise SystemExit("ABORT: Second Qualifying draw does not contain 160 unique draw slots")

confirmed_winners = []
unresolved = []
eliminated = set()
for f in first:
    r = latest_first_qualifying_result(data, f)
    winner = decisive_winner(r)
    if winner:
        confirmed_winners.append(winner)
        loser = f["away"] if norm(winner) == norm(f["home"]) else f["home"]
        eliminated.add(norm(loser))
    else:
        unresolved.append((f["home"], f["away"]))

# Every confirmed First Qualifying winner must occupy exactly one Second Qualifying slot.
used_side_indexes = set()
missing = []
for winner in confirmed_winners:
    hits = [i for i, s in enumerate(sides) if norm(s) == norm(winner)]
    if len(hits) != 1:
        missing.append(f"{winner} ({len(hits)} slots)")
    else:
        used_side_indexes.add(hits[0])
if missing:
    raise SystemExit("ABORT: confirmed First Qualifying winners not represented exactly once: " + ", ".join(missing[:12]))

# Each unresolved first-round tie must occupy one conditional draw slot containing both clubs.
unresolved_bad = []
for a, b in unresolved:
    hits = [i for i, s in enumerate(sides) if side_contains_both(s, a, b)]
    if len(hits) != 1:
        unresolved_bad.append(f"{a} / {b} ({len(hits)} conditional slots)")
    else:
        used_side_indexes.add(hits[0])
if unresolved_bad:
    raise SystemExit("ABORT: unresolved First Qualifying replay slots not represented exactly once: " + ", ".join(unresolved_bad[:12]))

# Any remaining draw slots are new Step 2 entrants. Eliminated First Qualifying teams
# may not reappear as standalone sides.
new_entrant_indexes = [i for i in range(len(sides)) if i not in used_side_indexes]
if len(new_entrant_indexes) != EXPECTED_NEW_ENTRANTS:
    raise SystemExit(
        f"ABORT: expected {EXPECTED_NEW_ENTRANTS} new Second Qualifying entrants, got {len(new_entrant_indexes)}"
    )
invalid_new = [sides[i] for i in new_entrant_indexes if norm(sides[i]) in eliminated]
if invalid_new:
    raise SystemExit("ABORT: eliminated First Qualifying clubs appear in Second Qualifying draw: " + ", ".join(invalid_new[:12]))

# Preserve old per-club fixture mappings, then let validated next-round fixtures replace
# mappings only for clubs/conditional participants involved in Second Qualifying.
fixture_map = dict(data.get("fixtures") or {})
for f in draw:
    f["conditional"] = bool(re.search(r"\s+or\s+", f["home"], re.I) or re.search(r"\s+or\s+", f["away"], re.I))
    add_fixture_mapping(fixture_map, f)

data["fixtures"] = fixture_map
data.setdefault("round_dates", {})[ROUND] = ROUND_DATE
data["updated_at"] = datetime.now(timezone.utc).isoformat()
data["second_qualifying_draw_sync"] = {
    "source": "The Football Association — Emirates FA Cup fixtures",
    "source_url": FA_FIXTURES_URL,
    "synced_at": data["updated_at"],
    "round": ROUND,
    "ties": len(draw),
    "confirmed_first_qualifying_winner_slots": len(confirmed_winners),
    "unresolved_replay_slots": len(unresolved),
    "new_entrants": len(new_entrant_indexes),
}

DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("SECOND QUALIFYING DRAW SYNC: SUCCESS")
print(f"Second Qualifying ties: {len(draw)}")
print(f"Confirmed First Qualifying winner slots: {len(confirmed_winners)}")
print(f"Unresolved replay slots: {len(unresolved)}")
print(f"New Step 2 entrants: {len(new_entrant_indexes)}")
print("Source: The FA Emirates FA Cup fixtures only")
print("First Qualifying chronology/results: PRESERVED")
print("Ground/location data: UNTOUCHED")
