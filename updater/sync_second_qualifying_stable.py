#!/usr/bin/env python3
"""Run the Second Qualifying draw sync without letting played rows erase the draw.

Once a draw slot is definite it is canonical. Live source rows are used only to
resolve still-conditional placeholders. This prevents match-day FT rows (which
legacy fixture parsing intentionally ignores) from shrinking the 80-tie draw.
"""
import json\n\nimport sync_second_qualifying_resolved as legacy


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


def main():
    legacy.reconcile_conditionals = reconcile_conditionals_stable
    legacy.main()


if __name__ == "__main__":
    main()
