#!/usr/bin/env python3
"""Regression: resolved draw slots survive when source fixture rows disappear."""
from sync_second_qualifying_stable import reconcile_conditionals_stable


def require(value, message):
    if not value:
        raise SystemExit("ACTIVE DRAW STABILITY REGRESSION: FAIL - " + message)


fixed = {"round": "Second Round Qualifying", "home": "Fixed Town", "away": "Settled United", "date": "2026-09-19"}
conditional = {"round": "Second Round Qualifying", "home": "Waiting Town", "away": "Alpha FC or Beta FC", "date": "2026-09-19"}
resolved = {"round": "Second Round Qualifying", "home": "Waiting Town", "away": "Beta FC", "date": "2026-09-19"}

final, retained, transitions, ambiguities = reconcile_conditionals_stable([], [fixed])
require(final == [fixed], "definite slot must survive an empty live fixture parse")
require(not retained and not transitions and not ambiguities, "fixed slot needs no conditional bookkeeping")

final, retained, transitions, ambiguities = reconcile_conditionals_stable([resolved], [fixed, conditional])
require(len(final) == 2, "fixed plus uniquely resolved conditional should retain full draw")
require(any(f["away"] == "Settled United" for f in final), "existing fixed slot must remain untouched")
require(any(f["away"] == "Beta FC" for f in final), "unique conditional resolution should be promoted")
require(len(transitions) == 1 and not retained and not ambiguities, "conditional transition should remain guarded")

print("ACTIVE DRAW STABILITY REGRESSION: PASS")
print("Played/source-disappeared fixed slot retained: PASS")
print("Conditional slot still resolves uniquely: PASS")
