#!/usr/bin/env python3
"""Build the one disposable canonical state used by the Pigeon Vale Final Boss."""
import json
from pathlib import Path
from auto_round_results import merge_disposition, merge_result, history_rows
from round_state_engine import classify_observation

OUT=Path("updater/pigeon-vale-catastrophe-candidate.json")
fixture={"round":"Fourth Round Qualifying","home":"Pigeon Vale","away":"Deterministic United","date":"2099-10-10"}
data={"schema_version":1,"updated_at":"2099-10-14T22:17:00Z","source_round":"Fourth Round Qualifying","fixtures":{},"result_history":{},"results":{},"match_events":[]}

played={"home":"Pigeon Vale","away":"Deterministic United","date":"2099-10-10","home_score":1,"away_score":1,"status":"FT(AET)","winner":"Pigeon Vale","decision":"penalties","venue":{"ground":"The Great Deterministic Boundary","postcode":"ZZ1 1ZZ","verification":"verified"},"source_url":"synthetic-authoritative-result"}
merge_result(data,classify_observation(fixture,played,history_rows(data))["result"])

ruling={"home":"Pigeon Vale","away":"Deterministic United","date":"2099-10-10","status":"VOID","decision":"voided-replay-ordered","source_url":"synthetic-governing-body-ruling"}
disp=classify_observation(fixture,ruling,history_rows(data))
if disp["kind"]!="disposition": raise SystemExit("FINAL BOSS: disposition not derived")
merge_disposition(data,disp["supersedes"],disp["result"])

replay_obs={"home":"Deterministic United","away":"Pigeon Vale","date":"2099-10-14","home_score":2,"away_score":2,"status":"FT(AET)","winner":"Deterministic United","decision":"penalties","venue":{"ground":"Tomorrow Stadium","postcode":"YY1 1YY","verification":"verified"},"source_url":"synthetic-authoritative-replay"}
merge_result(data,classify_observation(fixture,replay_obs,history_rows(data))["result"])

data["fixtures"]["future-wednesday-v-deterministic-united"]={"round":"First Round Proper","date":"2099-11-07","home":"Future Wednesday","away":"Deterministic United","venue":{"ground":"The Far Side of Tomorrow","postcode":"XX1 1XX","verification":"verified"}}
OUT.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print("FINAL BOSS STAGE 1 — OBSERVATION -> DISPOSABLE CANONICAL CANDIDATE: PASS")
