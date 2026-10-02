#!/usr/bin/env python3
"""Regression for generic active-round conditional fixture collapse."""
import urllib.error
from unittest.mock import patch
import auto_draw
from auto_draw import reconcile_active_conditionals, compatible, active_source_complete, unique_ties

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
final,transitions,metadata_updates,ambiguities=reconcile_active_conditionals(saved,official)
require(not ambiguities,"unique official resolutions must not be ambiguous")
require(len(transitions)==2,"both single- and double-conditional slots should collapse")
require(final[0]["home"]=="Beta FC" and "conditional" not in final[0],"single conditional did not collapse")
require(final[1]["home"]=="Delta" and final[1]["away"]=="Zeta AFC","double conditional did not collapse")
require(final[1]["kickoff"]=="12:30","official kickoff change was not promoted")
require(final[2]==saved[2],"ordinary fixture metadata must remain untouched when official metadata agrees")

definite_saved=[{"round":"Third Round Qualifying","home":"Brentwood Town","away":"Dagenham & Redbridge","date":"2026-10-03","kickoff":"15:00"}]
definite_official=[{"round":"Third Round Qualifying","home":"Brentwood Town","away":"Dagenham & Redbridge","date":"2026-10-03","kickoff":"12:30"}]
definite_final,definite_changes,definite_metadata,definite_ambiguities=reconcile_active_conditionals(definite_saved,definite_official)
require(not definite_ambiguities,"unique definite fixture metadata refresh must not be ambiguous")
require(definite_final[0]["home"]=="Brentwood Town" and definite_final[0]["away"]=="Dagenham & Redbridge","metadata refresh must never change participants")
require(definite_final[0]["kickoff"]=="12:30","definite active fixture must accept authoritative kickoff refresh")
require(not definite_changes,"definite metadata refresh must not be reported as a conditional resolution")
require(len(definite_metadata)==1,"definite metadata refresh must be reported separately")
require(definite_metadata[0]["changes"]==[{"field":"kickoff","from":"15:00","to":"12:30"}],"metadata report must show the exact kickoff change")


fa_row_html = """<tr><td>12:30</td><td>22</td><td>Brentwood Town</td><td>VS</td><td>Dagenham &amp; Redbridge</td><td>information</td></tr>"""
fa_context = "<h2>Saturday 3 October 2026 | Third Round Qualifying</h2>" + fa_row_html
parsed = auto_draw.parse_page(fa_context)
require(parsed and parsed[0]["kickoff"]=="12:30","explicit FA kickoff must be parsed, not defaulted")

duplicate_ties = auto_draw.unique_ties([
    {"round":"Third Round Qualifying","home":"Brentwood Town","away":"Dagenham & Redbridge","date":"2026-10-03","kickoff":"12:30"},
    {"round":"Third Round Qualifying","home":"Brentwood Town","away":"Dagenham & Redbridge","date":"2026-10-03","kickoff":""},
])
require(len(duplicate_ties)==1 and duplicate_ties[0]["kickoff"]=="12:30","duplicate FA row without kickoff must not overwrite explicit kickoff")


unresolved=[{"round":"Third Round Qualifying","home":"One or Two","away":"Three","conditional":True}]
final,transitions,_metadata,ambiguities=reconcile_active_conditionals(unresolved,[])
require(final==unresolved and not transitions and not ambiguities,"missing source evidence must retain placeholder")

amb_source=[
    {"round":"Third Round Qualifying","home":"One","away":"Three"},
    {"round":"Third Round Qualifying","home":"Two","away":"Three"},
]
final,transitions,_metadata,ambiguities=reconcile_active_conditionals(unresolved,amb_source)
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

noisy_duplicates=[
    {"round":"Third Round Qualifying","home":"Brentwood Town","away":"Dagenham & Redbridge","date":"2026-10-03","kickoff":"12:30"},
    {"round":"Third Round Qualifying\u200b","home":"Brentwood\u00a0Town","away":"Dagenham & Redbridge\ufeff","date":"2026-10-03","kickoff":""},
]
noisy_unique=unique_ties(noisy_duplicates)
require(len(noisy_unique)==1,"Unicode/HTML whitespace noise must not split one official fixture")
require(noisy_unique[0].get("kickoff")=="12:30","explicit kickoff must survive a noisy blank duplicate")

# Acceptance: the exact eleven stale Third Round Qualifying conditional slots
# present in protected main at PR creation must collapse as one set.
stale_trq = [
    {"round":"Third Round Qualifying","home":"Leamington or G'borough T","away":"Anstey Nomads","date":"2026-10-03","kickoff":"15:00","conditional":True},
    {"round":"Third Round Qualifying","home":"AFC Telford or Worksop","away":"FC United of Manchester","date":"2026-10-03","kickoff":"15:00","conditional":True},
    {"round":"Third Round Qualifying","home":"Bedford Town","away":"Hemel H or Win Finch","date":"2026-10-03","kickoff":"15:00","conditional":True},
    {"round":"Third Round Qualifying","home":"Brentwood Town","away":"Waltham A or Dag & Red","date":"2026-10-03","kickoff":"15:00","conditional":True},
    {"round":"Third Round Qualifying","home":"AFC Rushden & Diamonds","away":"Needham M or Braintree","date":"2026-10-03","kickoff":"15:00","conditional":True},
    {"round":"Third Round Qualifying","home":"Southall or Dorking Wanderers","away":"Chatham Town","date":"2026-10-03","kickoff":"15:00","conditional":True},
    {"round":"Third Round Qualifying","home":"Merthyr or Truro City","away":"Cirencester or Farnham","date":"2026-10-03","kickoff":"15:00","conditional":True},
    {"round":"Third Round Qualifying","home":"Cray Wands or Maidstone","away":"Yate Town or Chippenham","date":"2026-10-03","kickoff":"15:00","conditional":True},
    {"round":"Third Round Qualifying","home":"Hamp & Rich or Crowborough","away":"Weston SM or Wimborne","date":"2026-10-03","kickoff":"15:00","conditional":True},
    {"round":"Third Round Qualifying","home":"Uxbridge or Farnborough","away":"Hungerford Town","date":"2026-10-03","kickoff":"15:00","conditional":True},
    {"round":"Third Round Qualifying","home":"Thame Utd or Exmouth Town","away":"Eastbourne Borough","date":"2026-10-03","kickoff":"15:00","conditional":True},
]
resolved_trq = [
    {"round":"Third Round Qualifying","home":"Gainsborough Trinity","away":"Anstey Nomads","date":"2026-10-03","kickoff":"15:00"},
    {"round":"Third Round Qualifying","home":"Worksop Town","away":"FC United of Manchester","date":"2026-10-03","kickoff":"15:00"},
    {"round":"Third Round Qualifying","home":"Bedford Town","away":"Wingate & Finchley","date":"2026-10-03","kickoff":"15:00"},
    {"round":"Third Round Qualifying","home":"Brentwood Town","away":"Dagenham & Redbridge","date":"2026-10-03","kickoff":"12:30"},
    {"round":"Third Round Qualifying","home":"AFC Rushden & Diamonds","away":"Braintree Town","date":"2026-10-03","kickoff":"15:00"},
    {"round":"Third Round Qualifying","home":"Dorking Wanderers","away":"Chatham Town","date":"2026-10-03","kickoff":"15:00"},
    {"round":"Third Round Qualifying","home":"Truro City","away":"Cirencester Town","date":"2026-10-03","kickoff":"15:00"},
    {"round":"Third Round Qualifying","home":"Cray Wanderers","away":"Chippenham Town","date":"2026-10-03","kickoff":"15:00"},
    {"round":"Third Round Qualifying","home":"Crowborough Athletic","away":"Wimborne Town","date":"2026-10-03","kickoff":"15:00"},
    {"round":"Third Round Qualifying","home":"Uxbridge","away":"Hungerford Town","date":"2026-10-03","kickoff":"15:00"},
    {"round":"Third Round Qualifying","home":"Thame United","away":"Eastbourne Borough","date":"2026-10-03","kickoff":"15:00"},
]
accepted, accepted_transitions, accepted_metadata, accepted_ambiguities = reconcile_active_conditionals(stale_trq, resolved_trq)
require(not accepted_ambiguities, "eleven-slot TRQ acceptance set must resolve without ambiguity")
require(len(accepted_transitions) == 11, "all eleven stale TRQ conditional slots must collapse")
require(not accepted_metadata, "conditional acceptance set must not masquerade as definite metadata refresh")
require(all("conditional" not in fixture for fixture in accepted), "no conditional flag may survive eleven-slot acceptance")
expected_pairs = [(fixture["home"], fixture["away"]) for fixture in resolved_trq]
actual_pairs = [(fixture["home"], fixture["away"]) for fixture in accepted]
require(actual_pairs == expected_pairs, "eleven-slot TRQ participant identities must match the verified definite fixtures")
require(accepted[3]["kickoff"] == "12:30", "Brentwood acceptance fixture must carry authoritative 12:30 kickoff")
print("Eleven-slot TRQ acceptance: PASS")

print("Noisy duplicate fixture identity: PASS")

print("ACTIVE CONDITIONAL REFRESH REGRESSION: PASS")
print("Unique resolution: PASS")
print("Double-conditional resolution: PASS")
print("Official kickoff promotion: PASS")
print("Explicit FA kickoff parsing: PASS")
noisy_html = """<h3>Third Round Qualifying</h3><div>Saturday 3 October 2026</div><table><tr><td>12:30&quot;&gt;12:30</td><td>22</td><td>Brentwood Town</td><td>VS</td><td>Dagenham &amp; Redbridge</td></tr></table>"""
noisy_parsed = auto_draw.parse_page(noisy_html)
require(noisy_parsed and noisy_parsed[0].get("kickoff")=="12:30","kickoff must be extracted from noisy FA cell text")
print("Noisy FA kickoff parsing: PASS")
print("Duplicate kickoff preservation: PASS")
print("Ordinary fixture preservation: PASS")
print("Definite fixture metadata refresh: PASS")
print("Missing evidence retains placeholder: PASS")
print("Ambiguity fails closed: PASS")

print("Transient source retry: PASS")
print("Persistent source failure fails closed: PASS")
require(active_source_complete([{"tie": 1}, {"tie": 2}], 2),"complete active-round source must pass")
require(not active_source_complete([{"tie": 1}], 2),"partial active-round source must fail closed")
print("Active-round source completeness: PASS")
print("Real FA abbreviation forms: PASS")
