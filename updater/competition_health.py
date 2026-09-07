#!/usr/bin/env python3
import json,re
from datetime import datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'competition.json'
REPORT=ROOT/'competition-health.md'
JSON_REPORT=ROOT/'updater/competition-health.json'
UK=ZoneInfo('Europe/London')
GRACE_HOURS=3
MIN_PRELIMINARY_TIES=130
MIN_PRELIMINARY_RESULTS=130
EXPECTED_ACTIVE_TIES={'First Round Qualifying':112,'Second Round Qualifying':80,'Third Round Qualifying':40,'Fourth Round Qualifying':32,'First Round Proper':40,'Second Round Proper':20,'Third Round Proper':32,'Fourth Round Proper':16,'Fifth Round Proper':8,'Quarter Final':4,'Semi Final':2,'Final':1}

def norm(s):
    s=(s or '').lower().replace('&',' and ')
    s=re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
def dt_for(f):
    date=f.get('date')
    if not date:return None
    ko=f.get('kickoff') or '15:00'
    try:return datetime.fromisoformat(f'{date}T{ko}:00').replace(tzinfo=UK)
    except:return None
def unique_fixtures(data):
    found={}
    for section in ('preliminary_fixtures','fixtures','replays'):
        obj=data.get(section,{}) or {};vals=obj.values() if isinstance(obj,dict) else obj
        for f in vals:
            if not isinstance(f,dict) or not f.get('home') or not f.get('away'):continue
            key=(norm(f['home']),norm(f['away']),f.get('date',''),f.get('round',''));found.setdefault(key,{**f,'section':section})
    return list(found.values())
def all_results(data):
    out=[];seen=set()
    for r in (data.get('results',{}) or {}).values():
        if isinstance(r,dict):
            k=(norm(r.get('home')),norm(r.get('away')),r.get('date',''),r.get('home_score'),r.get('away_score'))
            if k not in seen:seen.add(k);out.append(r)
    for arr in (data.get('result_history',{}) or {}).values():
        if not isinstance(arr,list):continue
        for r in arr:
            if not isinstance(r,dict):continue
            k=(norm(r.get('home')),norm(r.get('away')),r.get('date',''),r.get('home_score'),r.get('away_score'))
            if k not in seen:seen.add(k);out.append(r)
    return out
def has_result(f,results):
    fh,fa=norm(f.get('home')),norm(f.get('away'));fd=f.get('date','')
    for r in results:
        if norm(r.get('home'))==fh and norm(r.get('away'))==fa:
            if fd and r.get('date') and fd!=r.get('date'):continue
            if r.get('home_score') is not None and r.get('away_score') is not None:return True
    return False
def unique_count(obj):
    vals=obj.values() if isinstance(obj,dict) else (obj or []);seen=set()
    for f in vals:
        if isinstance(f,dict) and f.get('home') and f.get('away'):seen.add((norm(f['home']),norm(f['away']),f.get('date',''),f.get('round','')))
    return len(seen)

data=json.loads(DATA.read_text(encoding='utf-8'));now=datetime.now(timezone.utc).astimezone(UK)
fixtures=unique_fixtures(data);results=all_results(data)
overdue=[];recent=[];upcoming=[];complete=[]
for f in fixtures:
    when=dt_for(f)
    if has_result(f,results):complete.append(f);continue
    if when is None:upcoming.append({**f,'health_note':'Date/time incomplete'});continue
    deadline=when+timedelta(hours=GRACE_HOURS)
    if now>deadline:overdue.append({**f,'scheduled':when.isoformat(),'deadline':deadline.isoformat()})
    elif now>=when:recent.append({**f,'scheduled':when.isoformat(),'deadline':deadline.isoformat()})
    else:upcoming.append({**f,'scheduled':when.isoformat()})

sync=data.get('competition_sync') or {}
prelim_ties=unique_count(data.get('preliminary_fixtures') or {})
prelim_results=len({(norm(r.get('home')),norm(r.get('away')),r.get('date',''),r.get('home_score'),r.get('away_score')) for r in results if str(r.get('round','')).startswith('Preliminary Round')})
round_archive=data.get('round_fixtures') or {}
firstq_source=round_archive.get('First Round Qualifying')
if firstq_source is None and data.get('source_round')=='First Round Qualifying':firstq_source=data.get('fixtures') or {}
firstq_ties=unique_count(firstq_source or {})
active_round=data.get('source_round','')
active_ties=unique_count(data.get('fixtures') or {})
active_unresolved=[]
vals=(data.get('fixtures') or {}).values() if isinstance(data.get('fixtures'),dict) else (data.get('fixtures') or [])
for f in vals:
    if isinstance(f,dict) and (f.get('conditional') or ' or ' in str(f.get('home','')).lower() or ' or ' in str(f.get('away','')).lower()):active_unresolved.append(f)
critical=[]
if not sync:critical.append('Canonical competition chronology has not been synchronised.')
if prelim_ties<MIN_PRELIMINARY_TIES:critical.append(f'Preliminary fixture coverage too low: {prelim_ties}.')
if prelim_results<MIN_PRELIMINARY_RESULTS:critical.append(f'Preliminary result/replay coverage too low: {prelim_results}.')
if firstq_ties!=112:critical.append(f'Archived First Qualifying fixture coverage is {firstq_ties}; expected 112.')
expected=EXPECTED_ACTIVE_TIES.get(active_round)
if expected is not None and active_ties!=expected:critical.append(f'{active_round} fixture coverage is {active_ties}; expected {expected}.')
if overdue:critical.append(f'{len(overdue)} played fixtures are overdue a result.')
payload={'checked_at':now.isoformat(),'grace_hours':GRACE_HOURS,'coverage':{'preliminary_unique_fixtures':prelim_ties,'preliminary_results_and_replays':prelim_results,'first_qualifying_unique_fixtures':firstq_ties,'active_round':active_round,'active_round_unique_fixtures':active_ties,'active_round_conditional_slots':len(active_unresolved)},'counts':{'known_fixtures':len(fixtures),'complete':len(complete),'awaiting_grace':len(recent),'overdue':len(overdue),'upcoming':len(upcoming),'critical':len(critical)},'critical':critical,'overdue':overdue,'awaiting_grace':recent,'competition_sync':sync}
JSON_REPORT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
lines=['# Tin Foil FA Cup — Competition Health','',f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S %Z')}**",'','## Chronology coverage','',f'- Preliminary Round ties known: **{prelim_ties}**',f'- Preliminary Round results/replays recorded: **{prelim_results}**',f'- First Qualifying Round ties preserved: **{firstq_ties} / 112**',f'- Active round: **{active_round or "Unknown"}**',f'- Active-round ties: **{active_ties}**',f'- Active-round conditional/replay slots: **{len(active_unresolved)}**','','## Fixture health','',f'- 🟢 Played fixtures with results: **{len(complete)}**',f'- 🟡 Recently played / grace period: **{len(recent)}**',f'- 🔴 Results requiring confirmation: **{len(overdue)}**',f'- ⚪ Upcoming / incomplete-date fixtures: **{len(upcoming)}**','']
if critical:lines += ['## 🔴 Critical competition-data issues','']+[f'- {x}' for x in critical]
else:lines += ['## 🟢 Competition chronology healthy','',f'Preliminary and First Qualifying chronology is preserved, the active **{active_round}** draw has canonical coverage, and no played fixture is overdue a result.']
if overdue:
    lines += ['','## Results requiring confirmation','']
    for f in sorted(overdue,key=lambda x:x.get('scheduled','')):lines.append(f"- **{f.get('home')} v {f.get('away')}** — {f.get('round','Round TBC')} — {f.get('date','Date TBC')} • {f.get('kickoff','15:00')}")
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('COMPETITION HEALTH v7.9.24')
print('Preliminary ties:',prelim_ties);print('Preliminary results/replays:',prelim_results);print('First Qualifying ties preserved:',firstq_ties);print('Active round:',active_round);print('Active ties:',active_ties);print('Active conditional/replay slots:',len(active_unresolved));print('RESULTS REQUIRING CONFIRMATION:',len(overdue));print('CRITICAL:',len(critical))
for x in critical:print('CRITICAL ITEM:',x)
print('Reports written: competition-health.md, updater/competition-health.json')
if critical:raise SystemExit(1)
