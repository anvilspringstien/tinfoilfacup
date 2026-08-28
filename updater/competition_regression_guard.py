#!/usr/bin/env python3
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'competition.json').read_text(encoding='utf-8'))
HTML=(ROOT/'clubfinder.html').read_text(encoding='utf-8')

def norm(s):
    s=(s or '').lower().replace('&',' and ')
    s=re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def all_results():
    out=[]; seen=set()
    for r in (DATA.get('results') or {}).values():
        if not isinstance(r,dict): continue
        k=(norm(r.get('home')),norm(r.get('away')),r.get('date',''),r.get('home_score'),r.get('away_score'))
        if k not in seen: seen.add(k); out.append(r)
    for arr in (DATA.get('result_history') or {}).values():
        if not isinstance(arr,list): continue
        for r in arr:
            if not isinstance(r,dict): continue
            k=(norm(r.get('home')),norm(r.get('away')),r.get('date',''),r.get('home_score'),r.get('away_score'))
            if k not in seen: seen.add(k); out.append(r)
    return out

results=all_results()

def require_result(home,away,hs,as_,date):
    for r in results:
        if norm(r.get('home'))==norm(home) and norm(r.get('away'))==norm(away) and r.get('home_score')==hs and r.get('away_score')==as_ and r.get('date')==date:
            return
    raise SystemExit(f'MISSING REGRESSION RESULT: {home} {hs}-{as_} {away} {date}')

# The three user-discovered regression regions plus replay resolution cases.
require_result('Lower Breck','Euxton Villa',3,2,'2026-08-22')
require_result('Wythenshawe','Clitheroe',3,1,'2026-08-22')
require_result('Heaton Stannington','Kendal Town',4,2,'2026-08-25')
require_result('Prescot Cables','Litherland Remyca',1,0,'2026-08-25')
require_result('Frenford','Haringey Borough',3,2,'2026-08-25')

prelim=DATA.get('preliminary_fixtures') or {}
unique={}
vals=prelim.values() if isinstance(prelim,dict) else prelim
for f in vals:
    if isinstance(f,dict) and f.get('home') and f.get('away'):
        unique[(norm(f['home']),norm(f['away']),f.get('date',''))]=f
if len(unique)<130:
    raise SystemExit(f'PRELIMINARY FIXTURE COVERAGE TOO LOW: {len(unique)}')

fixtures=DATA.get('fixtures') or {}
vals=fixtures.values() if isinstance(fixtures,dict) else fixtures
future=[]
for f in vals:
    if not isinstance(f,dict) or not f.get('home') or not f.get('away'): continue
    future.append(f)
    if f.get('conditional') or ' or ' in f.get('home','').lower() or ' or ' in f.get('away','').lower():
        raise SystemExit(f'UNRESOLVED FIRST QUALIFYING FIXTURE: {f.get("home")} v {f.get("away")}')
if len({(norm(f['home']),norm(f['away']),f.get('date','')) for f in future})!=112:
    raise SystemExit('FIRST QUALIFYING FIXTURE COVERAGE IS NOT 112 TIES')

if 's.next.drawUrl' in HTML:
    raise SystemExit('BROKEN NEXT-ROUND LINK PROPERTY STILL PRESENT')
if "esc(k.round||next.name)" not in HTML:
    raise SystemExit('KNOWN FIXTURE ROUND LABEL DOES NOT USE LIVE FIXTURE ROUND')

print('COMPETITION REGRESSION GUARD: PASS')
print('Preliminary ties:',len(unique))
print('First Qualifying ties:',len({(norm(f['home']),norm(f['away']),f.get('date','')) for f in future}))
print('Representative chronology results: PASS')
