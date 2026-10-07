#!/usr/bin/env python3
"""Regression for next-round advancement evidence."""
from reconcile_next_round_advancement import resolve

def req(ok,msg):
    if not ok: raise SystemExit("NEXT-ROUND ADVANCEMENT REGRESSION: FAIL - "+msg)

base={
 "source_round":"Fourth Round Qualifying",
 "fixtures":{
   "fylde":{"round":"Fourth Round Qualifying","home":"AFC Fylde","away":"Atherton Collieries","date":"2026-10-17"},
   "other":{"round":"Fourth Round Qualifying","home":"Other Town","away":"Elsewhere","date":"2026-10-17"},
 },
 "replays":{
   "a":{"round":"Third Round Qualifying Replay","home":"Atherton Collieries","away":"Trafford","date":"2026-10-06","kickoff":"19:45"}
 },
 "results":{},"result_history":{}
}
resolved,retained,ambiguous=resolve(base)
req(len(resolved)==1 and resolved[0]["winner"]=="Atherton Collieries","definite next-round participant must resolve replay winner")
req(resolved[0]["home_score"] is None and resolved[0]["away_score"] is None,"advancement evidence must never invent a score")
req(resolved[0]["decision"]=="next-round-fixture","evidence provenance must be explicit")
req(not retained and not ambiguous,"unique evidence should resolve cleanly")

missing={**base,"fixtures":{"other":base["fixtures"]["other"]}}
resolved,retained,ambiguous=resolve(missing)
req(not resolved and len(retained)==1 and not ambiguous,"missing evidence must fail closed")

both={**base,"fixtures":{
 "one":{"round":"Fourth Round Qualifying","home":"AFC Fylde","away":"Atherton Collieries"},
 "two":{"round":"Fourth Round Qualifying","home":"Trafford","away":"Other Town"},
}}
resolved,retained,ambiguous=resolve(both)
req(not resolved and len(ambiguous)==1,"both participants advancing must be ambiguous")

completed={**base,"results":{"Atherton Collieries":{"round":"Third Round Qualifying Replay","home":"Atherton Collieries","away":"Trafford","home_score":3,"away_score":0,"winner":"Atherton Collieries","status":"FT","date":"2026-10-06"}}}
resolved,retained,ambiguous=resolve(completed)
req(not resolved,"real scoreline must supersede advancement inference")

print("NEXT-ROUND ADVANCEMENT REGRESSION: PASS")
print("Unique official advancement: PASS")
print("No score fabrication: PASS")
print("Missing evidence fails closed: PASS")
print("Ambiguity fails closed: PASS")
print("Published result supersedes inference: PASS")
