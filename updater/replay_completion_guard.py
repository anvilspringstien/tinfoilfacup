#!/usr/bin/env python3
"""Fail closed if First Qualifying replay state is incomplete or inconsistent.

The 112 First Qualifying ties contain a fixed number of drawn first legs, but
the number of completed replays is allowed to increase naturally. Any draw
without a decisive replay must still be represented by a conditional slot in
the Second Qualifying draw. Once a decisive replay appears, the winner must be
linked into the next round and the old conditional slot must disappear.
"""
import json
import re
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
ROUND = "First Round Qualifying"
REPLAY_ROUND = ROUND + " Replay"
EXPECTED_TIES = 112
EXPECTED_DRAWS = 32


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"\b(fc|afc|cfc)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


LEGACY_NAME_ALIASES = {
    norm("Burgess H"): norm("Burgess Hill Town"),
    norm("Burgess Hill"): norm("Burgess Hill Town"),
}


def canonical_norm(s):
    n = norm(s)
    return LEGACY_NAME_ALIASES.get(n, n)


def pair_key(a, b):
    return tuple(sorted((canonical_norm(a), canonical_norm(b))))


def compatible(a, b):
    a, b = canonical_norm(a), canonical_norm(b)
    return bool(a and b and (a == b or a.startswith(b + " ") or b.startswith(a + " ")))


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
            canonical_norm(r.get("home")),
            canonical_norm(r.get("away")),
            r.get("date", ""),
            str(r.get("round") or "").lower(),
            score_int(r.get("home_score")),
            score_int(r.get("away_score")),
        )
        if ident not in seen:
            seen.add(ident)
            out.append(r)
    return out


def archived_ties(data):
    src = (data.get("round_fixtures") or {}).get(ROUND)
    ties = [f for f in fixture_values(src) if isinstance(f, dict) and f.get("home") and f.get("away")]
    if len(ties) != EXPECTED_TIES:
        raise SystemExit(
            f"REPLAY COMPLETION GUARD: FAIL - expected {EXPECTED_TIES} archived First Qualifying ties, found {len(ties)}"
        )
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


def conditional_alternatives(side):
    return [x.strip() for x in re.split(r"\s+or\s+", str(side or ""), flags=re.I) if x.strip()]


def conditional_pairs_in_next_round(data):
    """Return every two-club alternative pair still present in the active draw."""
    found = set()
    for src in second_round_sources(data):
        for f in fixture_values(src):
            if not isinstance(f, dict):
                continue
            for side in (f.get("home", ""), f.get("away", "")):
                alts = conditional_alternatives(side)
                if len(alts) < 2:
                    continue
                canonical = sorted({canonical_norm(x) for x in alts if canonical_norm(x)})
                for a, b in combinations(canonical, 2):
                    found.add(tuple(sorted((a, b))))
    return found


def winner_in_next_round(data, winner):
    for src in second_round_sources(data):
        for f in fixture_values(src):
            if not isinstance(f, dict):
                continue
            if compatible(f.get("home"), winner) or compatible(f.get("away"), winner):
                return True
            for side in (f.get("home", ""), f.get("away", "")):
                alts = conditional_alternatives(side)
                if len(alts) > 1 and sum(1 for x in alts if compatible(x, winner)) == 1:
                    return True
    return False


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    rows = all_results(data)
    draws = drawn_ties(data, rows)
    if len(draws) != EXPECTED_DRAWS:
        raise SystemExit(
            f"REPLAY COMPLETION GUARD: FAIL - expected {EXPECTED_DRAWS} First Qualifying draws, found {len(draws)}"
        )

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

    unresolved = set(draws) - set(replays)
    conditional_pairs = conditional_pairs_in_next_round(data)

    missing_placeholders = unresolved - conditional_pairs
    if missing_placeholders:
        raise SystemExit(
            "REPLAY COMPLETION GUARD: FAIL - unresolved First Qualifying replay(s) are not represented by a conditional Second Qualifying slot: "
            + "; ".join(" / ".join(x) for x in sorted(missing_placeholders))
        )

    stale_placeholders = set(replays) & conditional_pairs
    if stale_placeholders:
        raise SystemExit(
            "REPLAY COMPLETION GUARD: FAIL - resolved First Qualifying replay(s) still have stale conditional Second Qualifying slots: "
            + "; ".join(" / ".join(x) for x in sorted(stale_placeholders))
        )

    unlinked = sorted(winner for _, winner in replays.values() if not winner_in_next_round(data, winner))
    if unlinked:
        raise SystemExit(
            "REPLAY COMPLETION GUARD: FAIL - completed replay winners absent from Second Qualifying draw: "
            + ", ".join(unlinked)
        )

    print("REPLAY COMPLETION GUARD: PASS")
    print("Archived First Qualifying ties:", EXPECTED_TIES)
    print("Drawn first legs:", len(draws))
    print("Decisive completed replays:", len(replays))
    print("Pending unresolved replays:", len(unresolved))
    if unresolved:
        for pair in sorted(unresolved):
            print("PENDING:", " / ".join(pair))
    print("Completed replay winners linked to Second Qualifying:", len(replays))


if __name__ == "__main__":
    main()
