#!/usr/bin/env python3
"""Resolve overdue qualifying replays from a definite official next-round fixture.

This is a producer-side bridge, not a score guess. When the canonical active
round is exactly one round after an unresolved replay, and exactly one replay
participant appears in the definite active draw, the FA fixture catalogue has
authoritatively proved advancement. Record that winner while leaving scores
unknown. A later published scoreline may supersede this evidence naturally.
"""
import json,re
from datetime import datetime,timezone
from pathlib import Path
from round_state_engine import base_round,norm

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"competition.json"
REPORT=ROOT/"updater"/"next-round-advancement-report.json"
OFFICIAL_SOURCE="https://www.thefa.com/competitions/thefacup/fixtures"
ROUND_ORDER=["Extra Preliminary Round","Preliminary Round","First Round Qualifying","Second Round Qualifying","Third Round Qualifying","Fourth Round Qualifying","First Round Proper","Second Round Proper","Third Round Proper","Fourth Round Proper","Fifth Round Proper","Quarter Final","Semi Final","Final"]

def values(obj):
    return [x for x in (obj.values() if isinstance(obj,dict) else obj or []) if isinstance(x,dict)]

def pair(row):
    return {norm(row.get("home")),norm(row.get("away"))}-{""}

def score(v):
    return v if isinstance(v,int) else None

def all_results(data):
    out=[]
    for row in values(data.get("results")): out.append(row)
    for arr in (data.get("result_history") or {}).values():
        if isinstance(arr,list): out.extend(x for x in arr if isinstance(x,dict))
    return out

def terminal_replay_exists(results,replay):
    p=pair(replay); rnd=base_round(replay.get("round"))
    for r in results:
        if pair(r)!=p or base_round(r.get("round"))!=rnd: continue
        if not str(r.get("round") or "").lower().endswith(" replay"): continue
        hs,aw=score(r.get("home_score")),score(r.get("away_score"))
        if hs is not None and aw is not None and hs!=aw:
            return True
        if r.get("winner") and str(r.get("decision") or "").lower()!="next-round-fixture":
            return True
    return False

def active_clubs(data):
    clubs={}
    for f in values(data.get("fixtures")):
        # Conditional current fixtures are not definite advancement evidence.
        if f.get("conditional") or " or " in str(f.get("home","")).lower() or " or " in str(f.get("away","")).lower():
            continue
        for side in ("home","away"):
            n=norm(f.get(side))
            if n: clubs.setdefault(n,[]).append(f)
    return clubs

def aliases(name):
    name=str(name or "").strip(); out={name}
    suffix=re.compile(r"\s+(FC|AFC|CFC)$",re.I)
    out.add(suffix.sub("",name))
    if name and not suffix.search(name):
        out |= {name+" FC",name+" AFC"}
    return {x for x in out if x}

def merge_evidence(data,row):
    changed=False
    for club in aliases(row["home"])|aliases(row["away"]):
        arr=data.setdefault("result_history",{}).setdefault(club,[])
        same=next((x for x in arr if isinstance(x,dict) and pair(x)==pair(row) and str(x.get("date") or "")==row["date"] and str(x.get("decision") or "")=="next-round-fixture"),None)
        if not same:
            arr.append(dict(row)); changed=True
        data.setdefault("results",{})[club]=dict(row)
    return changed

def resolve(data):
    current=base_round(data.get("source_round"))
    if current not in ROUND_ORDER: return [],[],[]
    ci=ROUND_ORDER.index(current)
    if ci==0: return [],[],[]
    previous=ROUND_ORDER[ci-1]
    active=active_clubs(data)
    results=all_results(data)
    replays=[]
    seen=set()
    for r in values(data.get("replays")):
        if base_round(r.get("round"))!=previous: continue
        k=(tuple(sorted(pair(r))),str(r.get("date") or ""))
        if k not in seen: seen.add(k); replays.append(r)
    resolved=[]; retained=[]; ambiguous=[]
    for replay in replays:
        if terminal_replay_exists(results,replay): continue
        participants=[replay.get("home"),replay.get("away")]
        hits=[]
        for club in participants:
            n=norm(club)
            if n in active: hits.append((club,active[n]))
        if len(hits)==0:
            retained.append({"fixture":f'{replay.get("home")} v {replay.get("away")}','reason':"no participant in definite next-round draw"})
            continue
        if len(hits)>1:
            ambiguous.append({"fixture":f'{replay.get("home")} v {replay.get("away")}','participants_in_next_round':[x[0] for x in hits]})
            continue
        winner,fixtures=hits[0]
        evidence={
            "round":previous+" Replay",
            "home":replay.get("home"),"away":replay.get("away"),
            "home_score":None,"away_score":None,
            "winner":winner,
            "status":"ADVANCEMENT_CONFIRMED",
            "decision":"next-round-fixture",
            "date":replay.get("date",""),
            "source_url":OFFICIAL_SOURCE,
            "evidence_round":current,
            "evidence_fixture":f'{fixtures[0].get("home")} v {fixtures[0].get("away")}',
        }
        resolved.append(evidence)
    return resolved,retained,ambiguous

def main():
    data=json.loads(DATA.read_text(encoding="utf-8"))
    resolved,retained,ambiguous=resolve(data)
    if ambiguous:
        raise SystemExit("NEXT-ROUND ADVANCEMENT: ABORT - ambiguous evidence: "+str(ambiguous))
    changed=False
    for row in resolved: changed=merge_evidence(data,row) or changed
    if changed:
        data["updated_at"]=datetime.now(timezone.utc).isoformat()
        DATA.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    REPORT.write_text(json.dumps({"checked_at":datetime.now(timezone.utc).isoformat(),"status":"PASS","source_url":OFFICIAL_SOURCE,"resolved":resolved,"retained":retained,"ambiguous":ambiguous,"competition_changed":changed},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("NEXT-ROUND ADVANCEMENT: PASS")
    print("Resolved from definite next-round fixtures:",len(resolved))
    for r in resolved: print("ADVANCED:",r["home"],"v",r["away"],"->",r["winner"],"|",r["evidence_fixture"])
    print("Retained unresolved:",len(retained))
    print("Competition data changed:",changed)

if __name__=="__main__": main()
