#!/usr/bin/env python3
"""Regression: production-first candidate keeps newer fixtures and history."""
import copy
from build_reconciliation_candidate import build
def state():
    return {"schema_version":1,"season":"2026-27","fixtures":{"bury":{"round":"Fourth Round Qualifying","home":"Bury","away":"Harrogate Town AFC","kickoff":"12:30"},"fylde":{"round":"Fourth Round Qualifying","home":"AFC Fylde","away":"Atherton Collieries","kickoff":"15:00"}},"replays":{"a":{"round":"Third Round Qualifying Replay","home":"Atherton Collieries","away":"Trafford","date":"2026-10-06"}},"result_history":{"Trafford":[{"round":"Third Round Qualifying","home":"Trafford","away":"Atherton Collieries","home_score":2,"away_score":2}]},"results":{}}
p=state()
adv={"round":"Third Round Qualifying Replay","home":"Atherton Collieries","away":"Trafford","date":"2026-10-06","home_score":None,"away_score":None,"winner":"Atherton Collieries","decision":"next-round-fixture","source_url":"https://www.thefa.com/competitions/thefacup/fixtures","evidence_round":"Fourth Round Qualifying","evidence_fixture":"AFC Fylde v Atherton Collieries"}
b=copy.deepcopy(p)
b["fixtures"]["bury"]["kickoff"]="15:00"
b["result_history"]["Trafford"].append(adv)
b["result_history"]["Atherton Collieries"]=[adv]
out,rows,issues=build(p,b)
assert not issues and len(rows)==1,(rows,issues)
assert out["fixtures"]==p["fixtures"],"Bury kickoff overwritten"
assert out["replays"]==p["replays"],"Replay records lost"
assert p["result_history"]["Trafford"][0] in out["result_history"]["Trafford"],"Draw history lost"
assert out["results"]["Trafford"]["winner"]=="Atherton Collieries"
again,rows,issues=build(out,b)
assert not issues and again==out,"Repeated reconciliation not idempotent"
newer=copy.deepcopy(p)
newer["results"]["Trafford"]={"round":"Fourth Round Qualifying","date":"2026-10-17","winner":"Another Club"}
out,rows,issues=build(newer,b)
assert not issues and out["results"]["Trafford"]==newer["results"]["Trafford"],"Newer result overwritten"
bad=copy.deepcopy(b);bad["result_history"]["Trafford"][-1]["home_score"]=3;bad["result_history"]["Atherton Collieries"][0]["home_score"]=3
out,rows,issues=build(p,bad)
assert out is None and issues,"Invented score allowed"
bad=copy.deepcopy(b);bad["fixtures"]["fylde"]["away"]="Trafford"
out,rows,issues=build(p,bad)
assert out is not None,"Candidate must validate against production fixtures, not BETA fixtures"
print("PRODUCTION-FIRST CANDIDATE REGRESSION: PASS (preservation, replay, history, idempotency, newer result, invented score, canonical evidence)")
