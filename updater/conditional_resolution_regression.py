#!/usr/bin/env python3
"""Synthetic regression tests for conditional draw-slot resolution.

These cases deliberately use invented clubs so the resolver's behaviour remains
tested independently of the current FA Cup round:

* no definite source match -> retain the conditional placeholder;
* exactly one definite match -> promote it automatically;
* more than one definite match -> report ambiguity and fail closed upstream.
"""
from sync_second_qualifying_resolved import reconcile_conditionals, fixture_label


def require(condition, message):
    if not condition:
        raise SystemExit("CONDITIONAL RESOLUTION REGRESSION: FAIL - " + message)


def slot():
    return {
        "round": "Second Round Qualifying",
        "home": "Fixed Town",
        "away": "Alpha FC or Beta FC",
        "date": "2026-09-19",
        "kickoff": "15:00",
    }


def definite(away):
    return {
        "round": "Second Round Qualifying",
        "home": "Fixed Town",
        "away": away,
        "date": "2026-09-19",
        "kickoff": "15:00",
    }


# 1) Still unresolved: preserve the placeholder unchanged in meaning.
final, retained, transitions, ambiguities = reconcile_conditionals([], [slot()])
require(len(final) == 1, "unresolved slot should remain in the final draw")
require(len(retained) == 1, "unresolved slot should be retained")
require(not transitions, "unresolved slot must not create a transition")
require(not ambiguities, "unresolved slot must not be ambiguous")
require(" or " in fixture_label(retained[0]).lower(), "retained slot should remain conditional")

# 2) Exactly one source match: replace the placeholder automatically.
resolved = [definite("Beta FC")]
final, retained, transitions, ambiguities = reconcile_conditionals(resolved, [slot()])
require(len(final) == 1, "uniquely resolved slot should produce one final fixture")
require(not retained, "uniquely resolved slot must not retain its placeholder")
require(len(transitions) == 1, "uniquely resolved slot should record one transition")
require(not ambiguities, "uniquely resolved slot must not be ambiguous")
require(final[0]["away"] == "Beta FC", "unique source winner should replace the alternative list")

# 3) Two possible source matches: never guess which one owns the slot.
resolved = [definite("Alpha FC"), definite("Beta FC")]
final, retained, transitions, ambiguities = reconcile_conditionals(resolved, [slot()])
require(len(ambiguities) == 1, "multiple valid matches must be reported as ambiguous")
require(not transitions, "ambiguous slot must not be promoted")

print("CONDITIONAL RESOLUTION REGRESSION: PASS")
print("Unresolved placeholder retained: PASS")
print("Unique resolution promoted automatically: PASS")
print("Ambiguous resolution fails closed: PASS")
