#!/usr/bin/env python3
"""Synthetic tests for canonical shadow replay advancement."""
from shadow_replay_advancement import shadow

def state():
    return {"schema_version":1,"season":"2026-27",
      "source_url":"https://www.thefa.com/competitions/thefacup/fixtures",
      "fixtures":{"next":{"round":"First Round Proper","home":"Future Winners","away":"Example United","date":"2026-11-07"}},
      "replays":{"tie":{"round":"Fourth Round Qualifying Replay","home":"Example Town","away":"Future Winners","date":"2026-10-20"}},
      "result_history":{},"results":{}}

data=state()
report,candidate=shadow(data)
assert report["status"]=="SHADOW_OK" and report["accepted"]==1,report
assert data["results"]=={},"shadow mutated canonical input"
data=state()
data["fixtures"]={}
report,candidate=shadow(data)
assert report["status"]=="SHADOW_OK" and report["accepted"]==0,report
data=state()
data["fixtures"]["other"]={"round":"First Round Proper","home":"Future Winners","away":"Another United","date":"2026-11-07"}
report,candidate=shadow(data)
assert report["status"]=="BLOCKED",report
data=state()
data["result_history"]={"Example Town":[{"round":"Fourth Round Qualifying Replay","home":"Example Town","away":"Future Winners","date":"2026-10-20","winner":"Example Town","home_score":1,"away_score":0}]}
report,candidate=shadow(data)
assert report["status"]=="BLOCKED",report
print("SHADOW PRODUCER REGRESSION: PASS")
