#!/usr/bin/env python3
"""Fail closed if First Qualifying replay state is incomplete or inconsistent.

As of 11 September 2026 the 112 First Qualifying ties contain 32 drawn first
legs. Thirty-one replays have been decided; Burgess Hill Town v Jersey Bulls is
the sole pending replay after its fixture was postponed to 15 September. The
active draw abbreviates Burgess Hill Town as "Burgess H" in the Hanwell Town
conditional slot; only that exact legacy abbreviation is accepted here.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
ROUND = "First Round Qualifying"
REPLAY_ROUND = ROUND + " Replay"
EXPECTED_TIES = 112
EXPECTED_DRAWS = 32
EXPECTED_DECIDED_REPLAYS = 31


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"\b(fc|afc|cfc)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def pair_key(a, b):
    return tuple(sorted((norm(a), norm(b))))

PENDING_PAIR = pair_key("Burgess Hill Town", "Jersey Bulls")


def compatible(a, b):
    a, b = norm(a), norm(b)
    return bool(a and b and (a == b or a.startswith(b + " ") or b.startswith(a + " ")))


def pending_alt_match(alt, want):
    a, w = norm(alt), norm(want)
    if w == norm("Burgess Hill Town"):
        return a in {norm("Burgess H"), norm("Burgess Hill"), norm("Burgess Hill Town")}
    return compatible(a, w)


def score_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


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
            str(r.get("round") or "").lower(), score_int(r.get("home_score")), score_int(r.get("away_score"))
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
            hs, aw = score_int(r.get("home_score")), score_int(r.get("away_score"))
            if hs is not None and aw is not None and hs == aw:
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


def pending_slot_present(data):
    for src in second_round_sources(data):
        for f in fixture_values(src):
            if not isinstance(f, dict):
                continue
            for fixed, conditional in ((f.get("home", ""), f.get("away", "")), (f.get("away", ""), f.get("home", ""))):
                if not compatible(fixed, "Hanwell Town"):
                    continue
                alts = [x.strip() for x in re.split(r"\s+or\s+", str(conditional), flags=re.I) if x.strip()]
                if len(alts) == 2 and any(pending_alt_match(a, "Burgess Hill Town") for a in alts) and any(pending_alt_match(a, "Jersey Bulls") for a in alts):
                    return True
    return False


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    rows = all_results(data)
    draws = drawn_ties(data, rows)
    if len(draws) != EXPECTED_DRAWS:
        raise SystemExit(f"REPLAY COMPLETION GUARD: FAIL - expected {EXPECTED_DRAWS} First Qualifying draws, found {len(draws)}")
    if PENDING_PAIR not in draws:
        raise SystemExit("REPLAY COMPLETION GUARD: FAIL - Burgess Hill Town v Jersey Bulls 0-0 first leg not present among drawn ties")

    replays = {}
    for r in rows:
        key = pair_key(r.get("home"), r.get("away"))
        if key not in draws:
            continue
        if str(r.get("round") or "").lower() != REPLAY_ROUND.lower():
            continue
        hs, aw = score_int(r.get("home_score")), score_int(r.get("away_score"))
        if hs is None or aw is None or hs == aw:
            continue
        winner = r.get("winner") or (r.get("home") if hs > aw else r.get("away"))
        replays[key] = (r, winner)

    if len(replays) != EXPECTED_DECIDED_REPLAYS:
        raise SystemExit(f"REPLAY COMPLETION GUARD: FAIL - expected {EXPECTED_DECIDED_REPLAYS} decisive completed replays, found {len(replays)}")

    missing = set(draws) - set(replays)
    if missing != {PENDING_PAIR}:
        raise SystemExit("REPLAY COMPLETION GUARD: FAIL - replay completion gap is not the sole postponed Burgess Hill Town / Jersey Bulls tie: " + "; ".join(" / ".join(x) for x in sorted(missing)))

    if not pending_slot_present(data):
        raise SystemExit("REPLAY COMPLETION GUARD: FAIL - postponed Burgess Hill Town / Jersey Bulls replay is not retained in Hanwell Town's Second Qualifying slot")

    unlinked = sorted(winner for _, winner in replays.values() if not winner_in_next_round(data, winner))
    if unlinked:
        raise SystemExit("REPLAY COMPLETION GUARD: FAIL - completed replay winners absent from Second Qualifying draw: " + ", ".join(unlinked))

    print("REPLAY COMPLETION GUARD: PASS")
    print("Archived First Qualifying ties:", EXPECTED_TIES)
    print("Drawn first legs:", len(draws))
    print("Decisive completed replays:", len(replays))
    print("Pending postponed replays: 1 (Burgess Hill Town v Jersey Bulls)")
    print("Completed replay winners linked to Second Qualifying:", len(replays))


if __name__ == "__main__":
    main()
