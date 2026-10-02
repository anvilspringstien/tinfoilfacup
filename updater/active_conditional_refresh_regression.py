#!/usr/bin/env python3
"""Regression for generic active-round conditional fixture collapse."""
import urllib.error
from unittest.mock import patch
import auto_draw
from auto_draw import reconcile_active_conditionals, compatible, active_source_complete

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

calls=[0]
class Response:
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self): return b"ok"
def flaky(*args,**kwargs):
    calls[0]+=1
    if calls[0] < 3:
        raise urllib.error.HTTPError("https://example.invalid",504,"Gateway Time-out",None,None)
    return Response()
with patch.object(auto_draw.urllib.request,"urlopen",side_effect=flaky), patch.object(auto_draw.time,"sleep") as sleep:
    require(auto_draw.fetch("https://example.invalid")=="ok","transient source failure should recover")
    require(calls[0]==3 and [c.args[0] for c in sleep.call_args_list]==[2,5],"retry schedule must be 2s then 5s")

calls[0]=0
def dead(*args,**kwargs):
    calls[0]+=1
    raise urllib.error.HTTPError("https://example.invalid",504,"Gateway Time-out",None,None)
with patch.object(auto_draw.urllib.request,"urlopen",side_effect=dead), patch.object(auto_draw.time,"sleep") as sleep:
    try:
        auto_draw.fetch("https://example.invalid")
        require(False,"persistent transient failure must fail closed")
    except urllib.error.HTTPError:
        pass
    require(calls[0]==3 and sleep.call_count==2,"persistent failure must stop after three attempts")


real_abbreviations=[
    ("G'borough T","Gainsborough Trinity"),
    ("Win Finch","Wingate & Finchley"),
    ("Dag & Red","Dagenham & Redbridge"),
    ("Cray Wands","Cray Wanderers"),
    ("Thame Utd","Thame United"),
]
for short,full in real_abbreviations:
    require(compatible(short,full),f"FA abbreviation not recognized: {short} -> {full}")
require(not compatible("Town United","Town Wanderers"),"unrelated club words must not match")
require(not compatible("T","Trinity"),"single-letter token must not match independently")
require(not compatible("G'borough X","Gainsborough Trinity"),"wrong contextual initial must not match")
require(not compatible("A T","Another Trinity"),"initial-only club name must not match without substantive evidence")
require(compatible("Win Finch","Wingate & Finchley"),"connective omission must preserve valid abbreviation match")
require(not compatible("Win Town","Wingate & Finchley"),"ignoring connective must not hide a mismatched substantive token")
require(compatible("Cray Wands","Cray Wanderers"),"guarded stem contraction must match")
require(not compatible("Cray Wands","Cray Waltham"),"shared short opening must not match unrelated token")
require(compatible("Thame Utd","Thame United"),"conventional Utd abbreviation must match")
require(not compatible("Thame Utd","Thame University"),"Utd must not become generic Ut-prefix matching")

print("ACTIVE CONDITIONAL REFRESH REGRESSION: PASS")
print("Unique resolution: PASS")
print("Double-conditional resolution: PASS")
print("Official kickoff promotion: PASS")
print("Ordinary fixture preservation: PASS")
print("Missing evidence retains placeholder: PASS")
print("Ambiguity fails closed: PASS")

print("Transient source retry: PASS")
print("Persistent source failure fails closed: PASS")
require(active_source_complete([{"tie": 1}, {"tie": 2}], 2),"complete active-round source must pass")
require(not active_source_complete([{"tie": 1}], 2),"partial active-round source must fail closed")
print("Active-round source completeness: PASS")
print("Real FA abbreviation forms: PASS")
