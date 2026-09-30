#!/usr/bin/env python3
"""Apply explicitly human-reviewed exceptional FA replay dispositions.

This is deliberately not a fuzzy repair path.  Each record must match the
persisted original result exactly, must carry an explicit FA replay-order
source, and must agree with the already-published downstream draw before any
competition state is changed.
"""
import json, re
from datetime import datetime, timezone
from pathlib import Path

from auto_round_results import merge_result
from round_state_engine import base_round, norm, pair_key

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"competition.json"
LEDGER=ROOT/"updater"/"exceptional-replay-dispositions.json"

def rows(src):
    return src.values() if isinstance(src,dict) else (src or [])

def fixture_values(src):
    return [x for x in rows(src) if isinstance(x,dict) and x.get("home") and x.get("away")]

def exact_original(row, expected):
    return (
        base_round(row.get("round"))==expected["round"]
        and str(row.get("date") or "")==expected["date"]
        and norm(row.get("home"))==norm(expected["home"])
        and norm(row.get("away"))==norm(expected["away"])
        and row.get("home_score")==expected["home_score"]
        and row.get("away_score")==expected["away_score"]
    )

def exact_downstream(row, expected):
    return (
        str(row.get("round") or "")==expected["round"]
        and str(row.get("date") or "")==expected["date"]
        and norm(row.get("home"))==norm(expected["home"])
        and norm(row.get("away"))==norm(expected["away"])
        and str(row.get("kickoff") or "15:00")==expected.get("kickoff","15:00")
    )

def all_history_rows(data):
    for bucket in (data.get("result_history") or {}).values():
        if isinstance(bucket,list):
            for row in bucket:
                if isinstance(row,dict):
                    yield row

def apply_one(data, item):
    if item.get("verification_state")!="human-reviewed-exception":
        raise SystemExit("Exceptional replay disposition is not human-reviewed: "+str(item.get("id")))
    if item.get("disposition")!="voided-replay-ordered" or not item.get("disposition_source_url"):
        raise SystemExit("Exceptional replay disposition lacks explicit replay-order evidence: "+str(item.get("id")))

    original=item["original"]
    replay=item["replay_result"]
    downstream=item["downstream"]

    downstream_matches=[f for f in fixture_values(data.get("fixtures") or {}) if exact_downstream(f,downstream)]
    unique={(f.get("round"),f.get("date"),norm(f.get("home")),norm(f.get("away")),f.get("kickoff","15:00")) for f in downstream_matches}
    if len(unique)!=1:
        raise SystemExit("Exceptional replay safety stop: downstream Third Qualifying slot is missing or ambiguous.")

    matching=[r for r in all_history_rows(data) if exact_original(r,original)]
    already_voided=[r for r in matching if str(r.get("status") or "").upper() in {"VOID","VOIDED"} and r.get("decision")=="voided-replay-ordered"]
    live_original=[r for r in matching if str(r.get("status") or "").upper().startswith("FT")]

    if not matching:
        raise SystemExit("Exceptional replay safety stop: exact original result not found.")

    changed=False
    for row in live_original:
        row["status"]="VOID"
        row["decision"]="voided-replay-ordered"
        row["winner"]=""
        row["disposition_source_url"]=item["disposition_source_url"]
        row["disposition_note"]=item.get("disposition_note","")
        changed=True

    # Mirror the void disposition into any current-result aliases still pointing
    # at the superseded 19 September score before promoting the replay result.
    for key,row in list((data.get("results") or {}).items()):
        if isinstance(row,dict) and exact_original(row,original):
            row["status"]="VOID"
            row["decision"]="voided-replay-ordered"
            row["winner"]=""
            row["disposition_source_url"]=item["disposition_source_url"]
            row["disposition_note"]=item.get("disposition_note","")
            changed=True

    replay=dict(replay)
    if norm(replay.get("winner"))!=norm(replay.get("home")) or replay.get("home_score")<=replay.get("away_score"):
        raise SystemExit("Exceptional replay safety stop: persisted replay winner contradicts score.")
    if merge_result(data,replay):
        changed=True

    return changed, len(live_original), len(already_voided)

def main():
    data=json.loads(DATA.read_text(encoding="utf-8"))
    ledger=json.loads(LEDGER.read_text(encoding="utf-8"))
    items=ledger.get("dispositions") or []
    if len(items)!=1:
        raise SystemExit("Exceptional replay safety stop: expected exactly one reviewed disposition.")

    changed=False
    for item in items:
        did,voided,already=apply_one(data,item)
        changed=changed or did
        print("Exceptional replay:",item["id"])
        print("Newly voided original history rows:",voided)
        print("Already-voided history rows:",already)
        print("Replay result:",item["replay_result"]["home"],item["replay_result"]["home_score"],"-",item["replay_result"]["away_score"],item["replay_result"]["away"])

    if changed:
        data["updated_at"]=datetime.now(timezone.utc).isoformat()
        DATA.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print("EXCEPTIONAL REPLAY DISPOSITION: APPLIED")
    else:
        print("EXCEPTIONAL REPLAY DISPOSITION: ALREADY APPLIED")

if __name__=="__main__":
    main()
