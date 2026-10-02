#!/usr/bin/env python3
"""Regression for generic active-round conditional fixture collapse."""
from auto_draw import reconcile_active_conditionals

def require(ok,msg):
    if not ok:
        raise SystemExit("ACTIVE CONDITIONAL REFRESH REGRESSION: FAIL - "+msg)

saved=[
    {"round":"Third Round Qualifying","home":"Alpha or Beta","away":"Fixed Town","date":"2026-10-03","kickoff":"15:00","conditional":True},
    {"round":"Third Round Qualifying","home":"Gamma or Delta","away":"Epsilon or Zeta","date":"2026-10-03","kickoff":"15:00","conditional":True},
    {"round":"Third Round Qualifying","home":"Stable Town","away":"Normal City","date":"2026-10-03","kickoff":"15:00","venue":{"postcode":"AA1 1AA"}},
]
official=[
    {"round":"Third Round Qualifying","home":"Beta FC","away":"Fixed Town","date":"2026-10-03","kickoff":"15:00"},
    {"round":"Third Round Qualifying","home":"Delta","away":"Zeta AFC","date":"2026-10-03","kickoff":"12:30"},
]
final,transitions,ambiguities=reconcile_active_conditionals(saved,official)
require(not ambiguities,"unique official resolutions must not be ambiguous")
require(len(transitions)==2,"both single- and double-conditional slots should collapse")
require(final[0]["home"]=="Beta FC" and "conditional" not in final[0],"single conditional did not collapse")
require(final[1]["home"]=="Delta" and final[1]["away"]=="Zeta AFC","double conditional did not collapse")
require(final[1]["kickoff"]=="12:30","official kickoff change was not promoted")
require(final[2]==saved[2],"ordinary fixture metadata must remain untouched")

unresolved=[{"round":"Third Round Qualifying","home":"One or Two","away":"Three","conditional":True}]
final,transitions,ambiguities=reconcile_active_conditionals(unresolved,[])
require(final==unresolved and not transitions and not ambiguities,"missing source evidence must retain placeholder")

amb_source=[
    {"round":"Third Round Qualifying","home":"One","away":"Three"},
    {"round":"Third Round Qualifying","home":"Two","away":"Three"},
]
final,transitions,ambiguities=reconcile_active_conditionals(unresolved,amb_source)
require(len(ambiguities)==1 and not transitions,"multiple compatible official fixtures must fail closed")

print("ACTIVE CONDITIONAL REFRESH REGRESSION: PASS")
print("Unique resolution: PASS")
print("Double-conditional resolution: PASS")
print("Official kickoff promotion: PASS")
print("Ordinary fixture preservation: PASS")
print("Missing evidence retains placeholder: PASS")
print("Ambiguity fails closed: PASS")
