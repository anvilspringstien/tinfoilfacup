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
alias=copy.deepcopy(p)
alias["fixtures"]["fylde-alias"]=copy.deepcopy(alias["fixtures"]["fylde"])
alias_out,alias_rows,alias_issues=build(alias,b)
assert not alias_issues and len(alias_rows)==1,"Fixture alias treated as ambiguous"
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
# Conflicting evidence for the same replay must block the whole candidate.
contradiction=copy.deepcopy(b)
conflicting=copy.deepcopy(adv)
conflicting["winner"]="Trafford"
contradiction["result_history"]["Trafford"].append(conflicting)
out,rows,issues=build(p,contradiction)
assert out is None and any("contradictory" in x for x in issues),issues

# A missing provenance field must not be inferred from other records.
for field in ("source_url","evidence_fixture","evidence_round"):
    missing=copy.deepcopy(b)
    for entries in missing["result_history"].values():
        for row in entries:
            if row.get("decision")=="next-round-fixture":row.pop(field,None)
    out,rows,issues=build(p,missing)
    assert out is None and issues,(field,issues)

# A scored or otherwise authoritative current replay cannot be overwritten.
authoritative=copy.deepcopy(p)
authoritative["results"]["Trafford"]={"round":"Third Round Qualifying Replay","home":"Atherton Collieries","away":"Trafford","date":"2026-10-06","home_score":1,"away_score":0,"winner":"Atherton Collieries"}
out,rows,issues=build(authoritative,b)
assert out is None and any("authoritative current" in x for x in issues),issues

# A second distinct next-round fixture makes the advancement ambiguous.
ambiguous=copy.deepcopy(p)
ambiguous["fixtures"]["other"]={"round":"Fourth Round Qualifying","home":"Atherton Collieries","away":"Another Club","date":"2026-10-17"}
out,rows,issues=build(ambiguous,b)
assert out is None and any("ambiguous" in x for x in issues),issues

# Future-round fixture evidence: no October-specific advancement logic.
future=copy.deepcopy(p)
future["fixtures"]={"future":{"round":"First Round Proper","home":"Example United","away":"Future Winners","date":"2026-11-07"}}
future["replays"]={"future-replay":{"round":"Fourth Round Qualifying Replay","home":"Future Winners","away":"Example Town","date":"2026-10-20"}}
future["result_history"]={"Example Town":[]}
future["results"]={}
future_adv={"round":"Fourth Round Qualifying Replay","home":"Future Winners","away":"Example Town","date":"2026-10-20","home_score":None,"away_score":None,"winner":"Future Winners","decision":"next-round-fixture","source_url":"https://www.thefa.com/competitions/thefacup/fixtures","evidence_round":"First Round Proper","evidence_fixture":"Example United v Future Winners"}
future_evidence=copy.deepcopy(future)
future_evidence["result_history"]={"Example Town":[future_adv],"Future Winners":[future_adv]}
out,rows,issues=build(future,future_evidence)
assert not issues and len(rows)==1 and out["results"]["Example Town"]["winner"]=="Future Winners",(rows,issues)
future_missing=copy.deepcopy(future)
future_missing["fixtures"]={}
out,rows,issues=build(future_missing,future_evidence)
assert out is None and issues,"Future-round advancement accepted without canonical fixture"

print("PRODUCTION-FIRST CANDIDATE REGRESSION: PASS (preservation, replay, history, idempotency, newer result, invented score, canonical evidence, contradictory winners, missing provenance, authoritative results, ambiguous fixtures, future-round success and rejection)")
