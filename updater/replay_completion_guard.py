#!/usr/bin/env python3
"""Fail closed if a completed First Qualifying replay is absent from canonical state.

This is deliberately source-independent: if the live replay source is temporarily
unavailable, Competition Health can still verify that the retained canonical
state contains all 31 drawn First Qualifying ties, 31 decisive replay results,
and a Second Qualifying fixture for every replay winner.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
ROUND = "First Round Qualifying"
REPLAY_ROUND = ROUND + " Replay"
EXPECTED_DRAWS = 31


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"\b(fc|afc|cfc)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def pair_key(a, b):
    return tuple(sorted((norm(a), norm(b))))


def compatible(a, b):
    a, b = norm(a), norm(b)
    return bool(a and b and (a == b or a.startswith(b + " ") or b.startswith(a + " ")))


def history_rows(data):
    seen, out = set(), []
    for rows in (data.get("result_history") or {}).values():
        if not isinstance(rows, list):
            continue
        for r in rows:
            if not isinstance(r, dict):
                continue
            ident = (
                norm(r.get("home")), norm(r.get("away")), r.get("date", ""),
                str(r.get("round") or "").lower(), r.get("home_score"), r.get("away_score")
            )
            if ident in seen:
                continue
            seen.add(ident)
            out.append(r)
    return out


def fixture_values(src):
    return src.values() if isinstance(src, dict) else (src or [])


def winner_in_next_round(data, winner):
    sources = [data.get("fixtures") or {}]
    rf = data.get("round_fixtures") or {}
    if "Second Round Qualifying" in rf:
        sources.append(rf["Second Round Qualifying"])
    for src in sources:
        for f in fixture_values(src):
            if not isinstance(f, dict):
                continue
            if compatible(f.get("home"), winner) or compatible(f.get("away"), winner):
                return True
            # Retained conditional draw slots are also acceptable when exactly
            # one alternative names the verified winner.
            for side in (f.get("home", ""), f.get("away", "")):
                alts = [x.strip() for x in re.split(r"\s+or\s+", str(side), flags=re.I) if x.strip()]
                if len(alts) > 1 and sum(1 for x in alts if compatible(x, winner)) == 1:
                    return True
    return False


def main():
    data = json.loads(DATA.read_text())
    rows = history_rows(data)

    draws = {}
    for r in rows:
        if str(r.get("round") or "").lower() != ROUND.lower():
            continue
        hs, aw = r.get("home_score"), r.get("away_score")
        if isinstance(hs, int) and isinstance(aw, int) and hs == aw:
            draws[pair_key(r.get("home"), r.get("away"))] = r

    if len(draws) != EXPECTED_DRAWS:
        raise SystemExit(f"REPLAY COMPLETION GUARD: FAIL - expected {EXPECTED_DRAWS} First Qualifying draws, found {len(draws)}")

    replays = {}
    for r in rows:
        if str(r.get("round") or "").lower() != REPLAY_ROUND.lower():
            continue
        key = pair_key(r.get("home"), r.get("away"))
        if key not in draws:
            continue
        hs, aw = r.get("home_score"), r.get("away_score")
        if not isinstance(hs, int) or not isinstance(aw, int) or hs == aw:
            continue
        winner = r.get("winner") or (r.get("home") if hs > aw else r.get("away"))
        replays[key] = (r, winner)

    missing = sorted(set(draws) - set(replays))
    if missing:
        raise SystemExit("REPLAY COMPLETION GUARD: FAIL - completed replay missing for: " + "; ".join(" / ".join(x) for x in missing))

    unlinked = sorted(winner for _, winner in replays.values() if not winner_in_next_round(data, winner))
    if unlinked:
        raise SystemExit("REPLAY COMPLETION GUARD: FAIL - replay winners absent from Second Qualifying draw: " + ", ".join(unlinked))

    print("REPLAY COMPLETION GUARD: PASS")
    print("First Qualifying draws:", len(draws))
    print("Decisive replays:", len(replays))
    print("Replay winners linked to Second Qualifying:", len(replays))


if __name__ == "__main__":
    main()
