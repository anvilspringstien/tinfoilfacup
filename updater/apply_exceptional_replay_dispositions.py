#!/usr/bin/env python3
"""Apply explicitly human-reviewed exceptional FA replay dispositions.

This is deliberately not a fuzzy repair path.  Each record needs exact
chronology, an explicit FA replay-order source and an already-published
downstream draw. A missing superseded replay requires the retained drawn tie
and an explicit score source.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from auto_round_results import merge_result
from round_state_engine import base_round, is_draw, is_terminal, norm, pair_key, same_result

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"competition.json"
LEDGER=ROOT/"updater"/"exceptional-replay-dispositions.json"

def rows(src):
    return src.values() if isinstance(src,dict) else (src or [])

def fixture_values(src):
    return [x for x in rows(src) if isinstance(x,dict) and x.get("home") and x.get("away")]

def exact_original(row, expected):
    return (
        str(row.get("round") or "")==expected["round"]
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

def downstream_fixture_rows(data, expected):
    """Return only the authoritative bucket for the reviewed downstream round.

    While that round is active it lives in fixtures. After round promotion the
    draw watcher archives it under round_fixtures/<round>. Never search newer
    active fixtures or unrelated historical buckets for an exceptional replay.
    """
    active = [f for f in fixture_values(data.get("fixtures") or {}) if str(f.get("round") or "") == expected["round"]]
    if active:
        return active
    archived = (data.get("round_fixtures") or {}).get(expected["round"])
    if archived:
        return fixture_values(archived)
    if expected["round"] == "Preliminary Round":
        return fixture_values(data.get("preliminary_fixtures") or {})
    return []

def apply_one(data, item):
    if item.get("verification_state")!="human-reviewed-exception":
        raise SystemExit("Exceptional replay disposition is not human-reviewed: "+str(item.get("id")))
    if item.get("disposition")!="voided-replay-ordered" or not item.get("disposition_source_url"):
        raise SystemExit("Exceptional replay disposition lacks explicit replay-order evidence: "+str(item.get("id")))

    original=item["original"]
    replay=item["replay_result"]
    downstream=item["downstream"]

    downstream_matches=[f for f in downstream_fixture_rows(data,downstream) if exact_downstream(f,downstream)]
    unique={(f.get("round"),f.get("date"),norm(f.get("home")),norm(f.get("away")),f.get("kickoff","15:00")) for f in downstream_matches}
    if len(unique)!=1 or norm(replay.get("winner")) not in pair_key(downstream):
        raise SystemExit("Exceptional replay safety stop: downstream slot is missing, ambiguous, or contradicts the winner.")
    if (pair_key(original)!=pair_key(replay) or replay.get("round")!=base_round(original["round"])+" Replay"
            or replay["date"]<=original["date"] or not is_terminal(replay)
            or norm(replay.get("winner"))!=norm(replay.get("home"))
            or replay["home_score"]<=replay["away_score"]):
        raise SystemExit("Exceptional replay safety stop: replacement does not match the reviewed tie and winner.")

    history = list(all_history_rows(data))
    if any(pair_key(row)==pair_key(replay) and row.get("date","")>original["date"]
           and base_round(row.get("round"))==base_round(replay["round"])
           and not (is_terminal(row) and same_result(row,replay)) for row in history):
        raise SystemExit("Exceptional replay safety stop: conflicting replacement result.")
    same_day = [row for row in history if pair_key(row)==pair_key(original)
                and row.get("date")==original["date"]
                and base_round(row.get("round"))==base_round(original["round"])]
    matching = [row for row in same_day if exact_original(row,original)]
    if len(matching)!=len(same_day):
        raise SystemExit("Exceptional replay safety stop: conflicting superseded result.")
    already_voided=[r for r in matching if str(r.get("status") or "").upper() in {"VOID","VOIDED"} and r.get("decision")=="voided-replay-ordered"]
    live_original=[r for r in matching if str(r.get("status") or "").upper().startswith("FT")]
    if len(already_voided)+len(live_original)!=len(matching):
        raise SystemExit("Exceptional replay safety stop: unrecognised superseded result state.")

    void_fields = {
        "status": "VOID",
        "decision": "voided-replay-ordered",
        "winner": "",
        "disposition_source_url": item["disposition_source_url"],
        "disposition_note": item.get("disposition_note", ""),
    }
    changed=False
    if not matching:
        drawn = item.get("drawn_tie") or {}
        if (not original["round"].endswith(" Replay") or not original.get("source_url")
                or drawn.get("round")!=base_round(original["round"])
                or pair_key(drawn)!=pair_key(original) or drawn.get("date","")>=original["date"]
                or not any(is_draw(row) and exact_original(row,drawn) for row in history)):
            raise SystemExit("Exceptional replay safety stop: exact original result or replay ancestry not found.")
        changed = merge_result(data,{**original,**void_fields})

    for row in live_original:
        row.update(void_fields)
        changed=True

    # Repair aliases still pointing to the superseded score before promotion.
    for row in (data.get("results") or {}).values():
        if isinstance(row,dict) and exact_original(row,original) and row.get("status")!="VOID":
            row.update(void_fields)
            changed=True

    if merge_result(data,replay):
        changed=True

    return changed, len(live_original), len(already_voided)

def main():
    data=json.loads(DATA.read_text(encoding="utf-8"))
    ledger=json.loads(LEDGER.read_text(encoding="utf-8"))
    items=ledger.get("dispositions") or []
    ids = [item.get("id") for item in items]
    if not ids or None in ids or len(set(ids))!=len(ids):
        raise SystemExit("Exceptional replay safety stop: missing or duplicate reviewed disposition IDs.")

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
