#!/usr/bin/env python3
"""Synthetic regression coverage for the shared FA Cup round-state engine."""
from round_state_engine import classify_observation


def require(value, message):
    if not value:
        raise SystemExit("ROUND STATE REGRESSION: FAIL - " + message)


def fixture(round_name="Second Round Qualifying"):
    return {"round": round_name, "home": "Alpha Town", "away": "Beta United", "date": "2026-09-19"}


def obs(date, home="Alpha Town", away="Beta United", hs=None, ass=None, status="FT", winner="", decision=""):
    return {"home": home, "away": away, "date": date, "home_score": hs, "away_score": ass, "status": status, "winner": winner, "decision": decision, "source_url": "synthetic"}


# Ordinary decisive original.
r = classify_observation(fixture(), obs("2026-09-19", hs=2, ass=0), [])
require(r["result"]["round"] == "Second Round Qualifying", "ordinary result must remain original")
require(r["result"]["winner"] == "Alpha Town", "scoreline must determine winner")

# Draw -> replay. Orientation is irrelevant to replay identity.
draw = classify_observation(fixture(), obs("2026-09-19", hs=1, ass=1), [])["result"]
require(draw["decision"] == "draw-replay", "qualifying draw must create replay ancestry")
reverse = classify_observation(fixture(), obs("2026-09-22", home="Beta United", away="Alpha Town", hs=0, ass=2), [draw])["result"]
require(reverse["round"].endswith(" Replay"), "later reversed match after a draw must be a replay")
same_orientation = classify_observation(fixture(), obs("2026-09-22", hs=3, ass=1), [draw])["result"]
require(same_orientation["round"].endswith(" Replay"), "replay classification must not depend on reversed venue orientation")

# Abandoned and postponed matches do not create replay ancestry; their later FT is original.
abandoned = classify_observation(fixture(), obs("2026-09-19", status="ABANDONED"), [])
require(abandoned["kind"] == "event", "abandonment must remain unresolved")
rearranged = classify_observation(fixture(), obs("2026-09-23", hs=2, ass=3), [])
require(rearranged["result"]["round"] == "Second Round Qualifying", "rearranged abandoned tie must complete the original")
postponed = classify_observation(fixture(), obs("2026-09-19", status="POSTPONED"), [])
require(postponed["kind"] == "event", "postponement must remain unresolved")

# Reverse orientation by itself is never proof of a replay.
reverse_original = classify_observation(fixture(), obs("2026-09-23", home="Beta United", away="Alpha Town", hs=0, ass=1), [])
require(reverse_original["result"]["round"] == "Second Round Qualifying", "reverse orientation without prior draw must remain original")

# Walkover: terminal without inventing a scoreline, but explicit winner required.
walkover = classify_observation(fixture(), obs("2026-09-19", status="AWARDED", winner="Alpha Town", decision="walkover"), [])
require(walkover["result"]["winner"] == "Alpha Town", "walkover winner must advance")
require(walkover["result"]["home_score"] is None, "walkover must not invent score")
try:
    classify_observation(fixture(), obs("2026-09-19", status="AWARDED"), [])
    raise SystemExit("ROUND STATE REGRESSION: FAIL - award without winner should fail closed")
except ValueError:
    pass

# Replay tied after 90/120 can be resolved by an explicit penalties winner.
penalty_replay = classify_observation(fixture(), obs("2026-09-22", hs=0, ass=0, winner="Beta United", decision="penalties"), [draw])["result"]
require(penalty_replay["winner"] == "Beta United" and penalty_replay["decision"] == "penalties", "penalty replay winner must resolve custody")

# Competition Proper has no replay ancestry: a level FT needs an explicit winner.
proper = fixture("First Round Proper")
try:
    classify_observation(proper, obs("2026-11-07", hs=1, ass=1), [])
    raise SystemExit("ROUND STATE REGRESSION: FAIL - proper-round level FT without winner should fail closed")
except ValueError:
    pass
proper_pen = classify_observation(proper, obs("2026-11-07", hs=1, ass=1, winner="Beta United", decision="penalties"), [])["result"]
require(proper_pen["round"] == "First Round Proper", "proper-round penalty result must not become a replay")

# Once a tie has a terminal result, a later different result is contradictory.
terminal = r["result"]
try:
    classify_observation(fixture(), obs("2026-09-22", hs=0, ass=1), [terminal])
    raise SystemExit("ROUND STATE REGRESSION: FAIL - later result after terminal outcome should fail closed")
except ValueError:
    pass

print("ROUND STATE REGRESSION: PASS")
print("Ordinary decisive result: PASS")
print("Draw -> replay ancestry (orientation independent): PASS")
print("Abandoned/postponed -> rearranged original: PASS")
print("Walkover/award without invented score: PASS")
print("Qualifying replay penalties: PASS")
print("Competition Proper no-replay rule: PASS")
print("Terminal chronology conflict fails closed: PASS")
