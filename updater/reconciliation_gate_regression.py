#!/usr/bin/env python3
"""Read-only reconciliation gate regression. Uses only synthetic competition data."""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT=Path(__file__).with_name("reconciliation_gate.py")

def dataset():
    return {
        "schema_version":1,"season":"2026-27","updated_at":"2026-10-08",
        "fixtures":{"bury":{"round":"Fourth Round Qualifying","home":"Bury","away":"Harrogate Town AFC","kickoff":"12:30"}},
        "result_history":{"Trafford":[{"round":"Third Round Qualifying","home":"Trafford","away":"Atherton Collieries","home_score":2,"away_score":2,"decision":"draw-replay"}]},
        "results":{}
    }

def run(prod,candidate):
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"production.json"; c=Path(td)/"candidate.json"
        p.write_text(json.dumps(prod)); c.write_text(json.dumps(candidate))
        proc=subprocess.run([sys.executable,str(SCRIPT),"--production",str(p),"--candidate",str(c)],capture_output=True,text=True)
        if not proc.stdout:
            raise AssertionError(proc.stderr)
        return proc.returncode,json.loads(proc.stdout)

def check(name,prod,candidate,expected,field=None):
    code,report=run(prod,candidate)
    assert code==expected,(name,report)
    assert report["status"]==("REVIEW_READY" if expected==0 else "BLOCKED"),(name,report)
    if field: assert report[field]>0,(name,report)
    print(name+": PASS")

p=dataset()
check("Identical snapshot",p,copy.deepcopy(p),0)
b=copy.deepcopy(p)
b["result_history"]["Trafford"].append({"round":"Third Round Qualifying Replay","home":"Atherton Collieries","away":"Trafford","date":"2026-10-06","home_score":None,"away_score":None,"winner":"Atherton Collieries","decision":"next-round-fixture","source_url":"https://www.thefa.com/competitions/thefacup/fixtures","evidence_fixture":"AFC Fylde v Atherton Collieries"})
check("Valid scoreless advancement",p,b,0)
bad=copy.deepcopy(b);bad["result_history"]["Trafford"][-1]["home_score"]=3
check("Invented score rejected",p,bad,1)
bad=copy.deepcopy(b);bad["result_history"]["Trafford"][-1].pop("evidence_fixture")
check("Missing provenance rejected",p,bad,1)
bad=copy.deepcopy(b);bad["fixtures"]["bury"]["kickoff"]="15:00"
check("Bury kickoff regression rejected",p,bad,1,"fixture_conflicts")
bad=copy.deepcopy(b);bad["result_history"]["Trafford"]=[]
check("Lost history rejected",p,bad,1,"production_history_keys_with_missing_entries")
bad=copy.deepcopy(b);bad["fixtures"]={}
check("Lost production fixture rejected",p,bad,1,"production_fixture_keys_missing")
bad=copy.deepcopy(b);bad["season"]="2027-28"
check("Season mismatch rejected",p,bad,1)
print("RECONCILIATION GATE REGRESSION: PASS (8 scenarios)")
