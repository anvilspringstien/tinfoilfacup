#!/usr/bin/env python3
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"

if len(sys.argv) < 7:
    raise SystemExit("Usage: assisted_result.py HOME AWAY HOME_SCORE AWAY_SCORE ROUND DATE [DECISION]")

home = sys.argv[1].strip()
away = sys.argv[2].strip()
home_score = int(sys.argv[3])
away_score = int(sys.argv[4])
round_name = sys.argv[5].strip()
date = sys.argv[6].strip()
decision = sys.argv[7].strip() if len(sys.argv) > 7 else ""

if home_score < 0 or away_score < 0:
    raise SystemExit("Scores cannot be negative.")

data = json.loads(DATA.read_text(encoding="utf-8"))

def norm(s):
    s=(s or "").lower().replace("&"," and ")
    s=re.sub(r"\b(fc|afc|cfc)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def candidate_known():
    candidates=[]
    for sec in ("fixtures","replays"):
        obj=data.get(sec,{}) or {}
        vals=obj.values() if isinstance(obj,dict) else obj
        for f in vals:
            if not isinstance(f,dict): continue
            if norm(f.get("home"))==norm(home) and norm(f.get("away"))==norm(away):
                candidates.append((sec,f))
    # Also permit a result if the same match already exists in result_history
    # (useful for correction/re-entry) but never permit completely unknown clubs/ties.
    history=data.get("result_history",{}) or {}
    for arr in history.values():
        if not isinstance(arr,list): continue
        for r in arr:
            if norm(r.get("home"))==norm(home) and norm(r.get("away"))==norm(away):
                candidates.append(("history",r))
    return candidates

known=candidate_known()
if not known:
    raise SystemExit(f"Validation failed: {home} v {away} is not a known fixture/replay/history match.")

winner=""
if home_score>away_score:
    winner=home
elif away_score>home_score:
    winner=away
else:
    if not decision:
        raise SystemExit("Level result requires a decision, e.g. draw-replay.")
    if decision.lower()!="draw-replay":
        m=re.search(r"winner\s*:\s*([^;]+)",decision,re.I)
        if m: winner=m.group(1).strip()

result={
    "home":home,
    "away":away,
    "home_score":home_score,
    "away_score":away_score,
    "winner":winner,
    "status":"FT",
    "decision":decision,
    "date":date,
    "round":round_name,
    "source_url":"assisted-confirmation"
}

def same(a,b):
    return (
        norm(a.get("home"))==norm(b.get("home")) and
        norm(a.get("away"))==norm(b.get("away")) and
        str(a.get("date",""))==str(b.get("date","")) and
        str(a.get("home_score",""))==str(b.get("home_score","")) and
        str(a.get("away_score",""))==str(b.get("away_score",""))
    )

def aliases(name):
    short=re.sub(r"\s+(FC|AFC|CFC)$","",name,flags=re.I)
    vals={name,short}
    if short==name:
        vals.add(name+" FC")
        vals.add(name+" AFC")
    return {x for x in vals if x}

history=data.setdefault("result_history",{})
results=data.setdefault("results",{})

for club in aliases(home)|aliases(away):
    arr=history.setdefault(club,[])
    if not any(same(x,result) for x in arr):
        arr.append(result)
    arr.sort(key=lambda x:x.get("date",""))
    results[club]=result

# A completed replay/winner supersedes replay-pending state.
if winner:
    replays=data.setdefault("replays",{})
    participant_norms={norm(home),norm(away)}
    for k in list(replays):
        rv=replays.get(k) or {}
        if norm(k) in participant_norms or (
            norm(rv.get("home")) in participant_norms and
            norm(rv.get("away")) in participant_norms
        ):
            replays.pop(k,None)

data["updated_at"]=datetime.now(timezone.utc).isoformat()
data["last_result"]={
    "home":home,"away":away,
    "home_score":home_score,"away_score":away_score,
    "winner":winner,"date":date,"round":round_name
}
data["last_result_mode"]="assisted"

tmp=DATA.with_suffix(".json.new")
tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
tmp.replace(DATA)

print(f"RECORDED: {home} {home_score}-{away_score} {away}")
print("Round:",round_name)
print("Winner:",winner or "No winner / replay required")
print("History preserved.")
print("competition.json updated.")
