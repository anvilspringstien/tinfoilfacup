#!/usr/bin/env python3
"""Regression guard for the replay defects exposed by postcode KT21 2HS.

This is intentionally data-level rather than postcode-distance logic: it locks
in the two custody/next-round chains that were previously stale while also
protecting the one genuinely unresolved First Qualifying replay.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"\b(fc|afc|cfc)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def compatible(a, b):
    a, b = norm(a), norm(b)
    return bool(a and b and (a == b or a.startswith(b + " ") or b.startswith(a + " ")))


def score_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def fixture_values(src):
    return list(src.values()) if isinstance(src, dict) else list(src or [])


def all_results(data):
    rows = []
    rows.extend((data.get("results") or {}).values())
    for history in (data.get("result_history") or {}).values():
        if isinstance(history, list):
            rows.extend(history)
    return [r for r in rows if isinstance(r, dict)]


def has_result(rows, home, hs, aw, away, round_name):
    for r in rows:
        if not compatible(r.get("home"), home) or not compatible(r.get("away"), away):
            continue
        if score_int(r.get("home_score")) != hs or score_int(r.get("away_score")) != aw:
            continue
        if str(r.get("round") or "").lower() != round_name.lower():
            continue
        expected_winner = home if hs > aw else away if aw > hs else ""
        if expected_winner and not compatible(r.get("winner"), expected_winner):
            continue
        return True
    return False


def active_fixtures(data):
    return [f for f in fixture_values(data.get("fixtures") or {}) if isinstance(f, dict)]


def has_fixture(fixtures, home, away):
    return any(compatible(f.get("home"), home) and compatible(f.get("away"), away) for f in fixtures)


def conditional_count(fixtures):
    seen = set()
    for f in fixtures:
        if not (" or " in str(f.get("home", "")).lower() or " or " in str(f.get("away", "")).lower()):
            continue
        seen.add((str(f.get("home", "")), str(f.get("away", "")), str(f.get("date", ""))))
    return len(seen)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    rows = all_results(data)
    fixtures = active_fixtures(data)
    failures = []

    if not has_result(rows, "AFC Whyteleafe", 2, 3, "Crowborough Athletic", "First Round Qualifying Replay"):
        failures.append("missing decisive AFC Whyteleafe 2-3 Crowborough Athletic replay")
    if not has_fixture(fixtures, "Hampton & Richmond Borough", "Crowborough Athletic"):
        failures.append("Crowborough Athletic not linked to Hampton & Richmond Borough")

    if not has_result(rows, "Welling United", 2, 1, "Faversham Town", "First Round Qualifying Replay"):
        failures.append("missing decisive Welling United 2-1 Faversham Town replay")
    if not has_fixture(fixtures, "Dulwich Hamlet", "Welling United"):
        failures.append("Welling United not linked to Dulwich Hamlet")

    if conditional_count(fixtures) != 1:
        failures.append(f"expected exactly 1 unresolved Second Qualifying conditional slot, found {conditional_count(fixtures)}")

    pending = [f for f in fixtures if compatible(f.get("home"), "Hanwell Town") and "jersey bulls" in norm(f.get("away"))]
    if not pending:
        failures.append("genuine Hanwell Town / Burgess Hill Town or Jersey Bulls pending slot not preserved")

    if failures:
        raise SystemExit("KT21 REPLAY REGRESSION: FAIL\n- " + "\n- ".join(failures))

    print("KT21 REPLAY REGRESSION: PASS")
    print("Crowborough Athletic -> Hampton & Richmond Borough: PASS")
    print("Welling United 2-1 Faversham Town -> Dulwich Hamlet: PASS")
    print("Single genuine pending replay slot preserved: PASS")


if __name__ == "__main__":
    main()
