#!/usr/bin/env python3
"""Fail closed if completed First Qualifying replays are absent from canonical state.

The guard is source-independent. It derives drawn ties from the archived 112
First Qualifying fixtures plus recorded scores, so legacy result rows do not need
a round label. All 31 draws must have a decisive replay and every replay winner
must be represented in the Second Qualifying draw.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
ROUND = "First Round Qualifying"
REPLAY_ROUND = ROUND + " Replay"
EXPECTED_TIES = 112
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


def fixture_values(src):
    return list(src.values()) if isinstance(src, dict) else list(src or [])


def all_results(data):
    seen, out, sources = set(), [], []
    sources.extend((data.get("results") or {}).values())
    for rows in (data.get("result_history") or {}).values():
        if isinstance(rows, list):
            sources.extend(rows)
    for r in sources:
        if not isinstance(r, dict):
            continue
        ident = (
            norm(r.get("home")), norm(r.get("away")), r.get("date", ""),
            str(r.get("round") or "").lower(), r.get("home_score"), r.get("away_score")
        )
        if ident not in seen:
            seen.add(ident)
            out.append(r)
    return out


def archived_ties(data):
    src = (data.get("round_fixtures") or {}).get(ROUND)
    ties = [f for f in fixture_values(src) if isinstance(f, dict) and f.get("home") and f.get("away")]
    if len(ties) != EXPECTED_TIES:
        raise SystemExit(f"REPLAY COMPLETION GUARD: FAIL - expected {EXPECTED_TIES} archived First Qualifying ties, found {len(ties)}")
    return {pair_key(f["home"], f["away"]): f for f in ties}


def drawn_ties(data, rows):
    ties = archived_ties(data)
    draws = {}
    for key, fixture in ties.items():
        for r in rows:
            if pair_key(r.get("home"), r.get("away")) != key:
                continue
            if "replay" in str(r.get("round") or "").lower():
                continue
            hs, aw = r.get("home_score"), r.get("away_score")
            if isinstance(hs, int) and isinstance(aw, int) and hs == aw:
                draws[key] = fixture
                break
    return draws


def second_round_sources(data):
    sources = [data.get("fixtures") or {}]
    rf = data.get("round_fixtures") or {}
    if "Second Round Qualifying" in rf:
        sources.append(rf["Second Round Qualifying"])
    return sources


def winner_in_next_round(data, winner):
    for src in second_round_sources(data):
        for f in fixture_values(src):
            if not isinstance(f, dict):
                continue
            if compatible(f.get("home"), winner) or compatible(f.get("away"), winner):
                return True
            for side in (f.get("home", ""), f.get("away", "")):
                alts = [x.strip() for x in re.split(r"\s+or\s+", str(side), flags=re.I) if x.strip()]
                if len(alts) > 1 and sum(1 for x in alts if compatible(x, winner)) == 1:
                    return True
    return False


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    rows = all_results(data)
    draws = drawn_ties(data, rows)
    if len(draws) != EXPECTED_DRAWS:
        raise SystemExit(f"REPLAY COMPLETION GUARD: FAIL - expected {EXPECTED_DRAWS} First Qualifying draws, found {len(draws)}")

    replays = {}
    for r in rows:
        key = pair_key(r.get("home"), r.get("away"))
        if key not in draws:
            continue
        if str(r.get("round") or "").lower() != REPLAY_ROUND.lower():
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
    print("Archived First Qualifying ties:", EXPECTED_TIES)
    print("First Qualifying draws:", len(draws))
    print("Decisive replays:", len(replays))
    print("Replay winners linked to Second Qualifying:", len(replays))


if __name__ == "__main__":
    main()
