#!/usr/bin/env python3
import json,re
from datetime import datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"competition.json"
REPORT=ROOT/"competition-health.md"
JSON_REPORT=ROOT/"updater/competition-health.json"
UK=ZoneInfo("Europe/London")
GRACE_HOURS=3

def norm(s):
    s=(s or "").lower().replace("&"," and ")
    s=re.sub(r"\b(fc|afc|cfc)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def dt_for(f):
    date=f.get("date")
    if not date:return None
    ko=f.get("kickoff") or "15:00"
    try:return datetime.fromisoformat(f"{date}T{ko}:00").replace(tzinfo=UK)
    except:return None

def unique_fixtures(data):
    found={}
    for section in ("fixtures","replays"):
        obj=data.get(section,{}) or {}
        vals=obj.values() if isinstance(obj,dict) else obj
        for f in vals:
            if not isinstance(f,dict) or not f.get("home") or not f.get("away"):continue
            key=(norm(f["home"]),norm(f["away"]),f.get("date",""),f.get("round",""))
            found.setdefault(key,{**f,"section":section})
    return list(found.values())

def all_results(data):
    out=[];seen=set()
    for r in (data.get("results",{}) or {}).values():
        if isinstance(r,dict):
            k=(norm(r.get("home")),norm(r.get("away")),r.get("date",""),r.get("home_score"),r.get("away_score"))
            if k not in seen:seen.add(k);out.append(r)
    for arr in (data.get("result_history",{}) or {}).values():
        if not isinstance(arr,list):continue
        for r in arr:
            if not isinstance(r,dict):continue
            k=(norm(r.get("home")),norm(r.get("away")),r.get("date",""),r.get("home_score"),r.get("away_score"))
            if k not in seen:seen.add(k);out.append(r)
    return out

def has_result(f,results):
    fh,fa=norm(f.get("home")),norm(f.get("away"))
    fd=f.get("date","")
    for r in results:
        if norm(r.get("home"))==fh and norm(r.get("away"))==fa:
            # Date is a strong check when both are present; tolerate absent date in legacy records.
            if fd and r.get("date") and fd!=r.get("date"):continue
            if r.get("home_score") is not None and r.get("away_score") is not None:
                return True
    return False

data=json.loads(DATA.read_text(encoding="utf-8"))
now=datetime.now(timezone.utc).astimezone(UK)
fixtures=unique_fixtures(data)
results=all_results(data)

overdue=[];recent=[];upcoming=[];complete=[]
for f in fixtures:
    when=dt_for(f)
    if has_result(f,results):
        complete.append(f);continue
    if when is None:
        upcoming.append({**f,"health_note":"Date/time incomplete"});continue
    deadline=when+timedelta(hours=GRACE_HOURS)
    if now>deadline:
        overdue.append({**f,"scheduled":when.isoformat(),"deadline":deadline.isoformat()})
    elif now>=when:
        recent.append({**f,"scheduled":when.isoformat(),"deadline":deadline.isoformat()})
    else:
        upcoming.append({**f,"scheduled":when.isoformat()})

payload={
 "checked_at":now.isoformat(),
 "grace_hours":GRACE_HOURS,
 "counts":{"known_fixtures":len(fixtures),"complete":len(complete),"awaiting_grace":len(recent),"overdue":len(overdue),"upcoming":len(upcoming)},
 "overdue":overdue,"awaiting_grace":recent
}
JSON_REPORT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

lines=[
 "# Tin Foil FA Cup — Competition Health",
 "",
 f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S %Z')}**",
 "",
 f"- 🟢 Results recorded: **{len(complete)}**",
 f"- 🟡 Recently played / grace period: **{len(recent)}**",
 f"- 🔴 Results requiring confirmation: **{len(overdue)}**",
 f"- ⚪ Upcoming / incomplete-date fixtures: **{len(upcoming)}**",
 "",
 "A result becomes overdue **3 hours after its scheduled kick-off** if no final score exists in `results` or `result_history`.",
 ""
]
if overdue:
    lines += ["## 🔴 Results requiring confirmation",""]
    for f in sorted(overdue,key=lambda x:x.get("scheduled","")):
        lines.append(f"- **{f.get('home')} v {f.get('away')}** — {f.get('round','Round TBC')} — {f.get('date','Date TBC')} • {f.get('kickoff','15:00')}")
else:
    lines += ["## 🟢 No overdue results","", "No known played fixture currently requires manual result confirmation."]

if recent:
    lines += ["","## 🟡 Grace period",""]
    for f in sorted(recent,key=lambda x:x.get("scheduled","")):
        lines.append(f"- {f.get('home')} v {f.get('away')} — waiting until {f.get('deadline','')} before flagging.")

REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8")

print("COMPETITION HEALTH v7.6.1")
print("Known unique fixtures:",len(fixtures))
print("Results recorded:",len(complete))
print("Grace period:",len(recent))
print("RESULTS REQUIRING CONFIRMATION:",len(overdue))
print("Upcoming/incomplete:",len(upcoming))
for f in overdue:
    print("MISSING",f.get("home"),"v",f.get("away"),"|",f.get("round"),"|",f.get("date"),f.get("kickoff","15:00"))
print("Reports written: competition-health.md, updater/competition-health.json")
