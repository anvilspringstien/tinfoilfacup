#!/usr/bin/env python3
"""One-time guarded repair for the three 9 September 2026 First Qualifying replays.

The hourly scanner historically matched canonical ties in home/away order, so
replays staged at the opposite venue could be invisible. The generic scanner fix
lives in auto_results.py; this repair closes the already-played round without
waiting for a source page to re-render its historical rows.

Safety: each replay is written only if its corresponding 5 September drawn first
leg is already present in canonical result_history/results. Existing identical
replay rows are left untouched. Conflicting decisive rows abort publication.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, re

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'competition.json'

def norm(s):
    s=(s or '').lower().replace('&',' and ')
    s=re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def aliases(n):
    suf=re.compile(r'\s+(FC|AFC|CFC)$',re.I)
    out={n,suf.sub('',n)}
    if not suf.search(n):out|={n+' FC',n+' AFC'}
    return {x for x in out if x}

def all_results(d):
    out=[];seen=set()
    for r in (d.get('results') or {}).values():
        if isinstance(r,dict):
            k=(norm(r.get('home')),norm(r.get('away')),r.get('date',''),r.get('home_score'),r.get('away_score'))
            if k not in seen:seen.add(k);out.append(r)
    for arr in (d.get('result_history') or {}).values():
        if not isinstance(arr,list):continue
        for r in arr:
            if not isinstance(r,dict):continue
            k=(norm(r.get('home')),norm(r.get('away')),r.get('date',''),r.get('home_score'),r.get('away_score'))
            if k not in seen:seen.add(k);out.append(r)
    return out

def same_score(r,home,away,hs,as_,date):
    return norm(r.get('home'))==norm(home) and norm(r.get('away'))==norm(away) and int(r.get('home_score',-999))==hs and int(r.get('away_score',-999))==as_ and r.get('date')==date

def same_pair(r,a,b):
    return {norm(r.get('home')),norm(r.get('away'))}=={norm(a),norm(b)}

def merge(d,r):
    for club in aliases(r['home'])|aliases(r['away']):
        arr=d.setdefault('result_history',{}).setdefault(club,[])
        if not any(same_score(x,r['home'],r['away'],r['home_score'],r['away_score'],r['date']) for x in arr):
            arr.append(dict(r))
            arr.sort(key=lambda x:(x.get('date',''),0 if 'Replay' not in str(x.get('round','')) else 1))
        d.setdefault('results',{})[club]=arr[-1]

repairs=[
    {
      'first':('Emley AFC','Bishop Auckland',1,1,'2026-09-05'),
      'replay':{'home':'Bishop Auckland','away':'Emley AFC','home_score':0,'away_score':2,'winner':'Emley AFC','status':'AET','decision':'aet','date':'2026-09-09','round':'First Round Qualifying Replay','source_url':'https://www.thefa.com/competitions/thefacup/results'}
    },
    {
      'first':('Crowborough Athletic','AFC Whyteleafe',1,1,'2026-09-05'),
      'replay':{'home':'AFC Whyteleafe','away':'Crowborough Athletic','home_score':2,'away_score':3,'winner':'Crowborough Athletic','status':'FT','decision':'','date':'2026-09-09','round':'First Round Qualifying Replay','source_url':'https://www.thefa.com/competitions/thefacup/results'}
    },
    {
      'first':('Banbury United','Exmouth Town',0,0,'2026-09-05'),
      'replay':{'home':'Exmouth Town','away':'Banbury United','home_score':2,'away_score':1,'winner':'Exmouth Town','status':'FT','decision':'','date':'2026-09-09','round':'First Round Qualifying Replay','source_url':'https://www.thefa.com/competitions/thefacup/results'}
    },
]

d=json.loads(DATA.read_text(encoding='utf-8'))
existing=all_results(d)
added=[]
for item in repairs:
    fh,fa,fhs,fas,fd=item['first']; rr=item['replay']
    if not any(same_score(x,fh,fa,fhs,fas,fd) for x in existing):
        raise SystemExit(f'ABORT: prerequisite first-leg draw missing: {fh} {fhs}-{fas} {fa} {fd}')
    exact=next((x for x in existing if same_score(x,rr['home'],rr['away'],rr['home_score'],rr['away_score'],rr['date'])),None)
    if exact:continue
    conflicts=[x for x in existing if same_pair(x,rr['home'],rr['away']) and x.get('date')==rr['date'] and (x.get('home_score'),x.get('away_score'))!=(rr['home_score'],rr['away_score'])]
    if conflicts:
        raise SystemExit(f"ABORT: conflicting replay result already present for {rr['home']} v {rr['away']}: {conflicts}")
    merge(d,rr); existing.append(rr); added.append(rr)

if added:
    d['updated_at']=datetime.now(timezone.utc).isoformat()
    DATA.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

print('FIRST QUALIFYING REPLAY REPAIR: PASS')
print('Added:',len(added))
for r in added:print(r['home'],r['home_score'],'-',r['away_score'],r['away'],'->',r['winner'])
