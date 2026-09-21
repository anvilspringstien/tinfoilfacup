#!/usr/bin/env python3
"""Run the Second Qualifying draw sync without letting played rows erase the draw.

Once a draw slot is definite it is canonical. Live source rows are used only to
resolve still-conditional placeholders. This prevents match-day FT rows (which
legacy fixture parsing intentionally ignores) from shrinking the 80-tie draw.
"""
import json

import sync_second_qualifying_resolved as legacy


def reconcile_conditionals_stable(resolved, current):
    fixed = [dict(f) for f in current if not legacy.is_conditional_fixture(f)]
    conditionals = [dict(f) for f in current if legacy.is_conditional_fixture(f)]
    if not current:
        return list(resolved), [], [], []

    retained = []
    promoted = []
    transitions = []
    ambiguities = []
    source_claims = {}

    for slot in conditionals:
        matches = [f for f in resolved if legacy.fixture_matches_slot(f, slot)]
        if len(matches) > 1:
            ambiguities.append({"slot": legacy.fixture_label(slot), "matches": [legacy.fixture_label(f) for f in matches]})
            continue
        if len(matches) == 1:
            match = matches[0]
            key = tuple(sorted((legacy.norm(match["home"]), legacy.norm(match["away"]))))
            if key in source_claims:
                ambiguities.append({
                    "slot": legacy.fixture_label(slot),
                    "matches": [legacy.fixture_label(match)],
                    "also_claimed_by": source_claims[key],
                })
                continue
            source_claims[key] = legacy.fixture_label(slot)
            promoted.append(dict(match))
            transitions.append({"from": legacy.fixture_label(slot), "to": legacy.fixture_label(match)})
            continue

        keep = dict(slot)
        keep.update({"round": legacy.ROUND, "date": legacy.DATE})
        retained.append(keep)

    return fixed + promoted + retained, retained, transitions, ambiguities


REQUIRED_CANARIES = [
    ("Hampton & Richmond Borough", "Crowborough Athletic"),
    ("Dulwich Hamlet", "Welling United"),
    ("Thame United", "Exmouth Town"),
    ("Needham Market", "Braintree Town"),
    ("Hemel Hempstead Town", "Wingate & Finchley"),
]


def main():
    data = json.loads(legacy.DATA.read_text(encoding="utf-8"))
    active_round = str(data.get("source_round") or "")

    # Once the competition advances, Second Qualifying is immutable history.
    # Never let this historical sync overwrite the later active draw.
    if active_round != legacy.ROUND:
        archived = legacy.unique_fixtures(
            (data.get("round_fixtures") or {}).get(legacy.ROUND) or {}
        )
        missing = [
            f"{a} v {b}"
            for a, b in REQUIRED_CANARIES
            if not legacy.has_fixture(archived, a, b)
        ]
        if len(archived) != legacy.EXPECTED_TOTAL or missing:
            legacy.fail(
                "archived_round",
                "SECOND QUALIFYING STABLE SYNC: ABORT - archived draw is incomplete after round advancement",
                active_round=active_round,
                archived_ties=len(archived),
                missing=missing,
            )
        legacy.report(
            "archived_round",
            status="PASS",
            active_round=active_round,
            archived_ties=len(archived),
            message="Second Qualifying archive verified; later active draw preserved.",
        )
        print("SECOND QUALIFYING STABLE SYNC: PASS")
        print("Active round has advanced:", active_round or "UNKNOWN")
        print("Archived Second Qualifying ties:", len(archived))
        print("Later active draw: UNTOUCHED")
        return

    legacy.reconcile_conditionals = reconcile_conditionals_stable
    legacy.main()


if __name__ == "__main__":
    main()
