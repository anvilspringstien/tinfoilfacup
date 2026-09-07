#!/usr/bin/env python3
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'competition.json').read_text(encoding='utf-8'))
HTML=(ROOT/'clubfinder.html').read_text(encoding='utf-8')

EXPECTED_ACTIVE_TIES={
    'First Round Qualifying':112,
    'Second Round Qualifying':80,
    'Third Round Qualifying':40,
    'Fourth Round Qualifying':32,
    'First Round Proper':40,
    'Second Round Proper':20,
    'Third Round Proper':32,
    'Fourth Round Proper':16,
    'Fifth Round Proper':8,
    'Quarter Final':4,
    'Semi Final':2,
    'Final':1,
}

def norm(s):
    s=(s or '').lower().replace('&',' and ')
    s=re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def unique_fixtures(src):
    vals=src.values() if isinstance(src,dict) else (src or [])
    out={}
    for f in vals:
        if not isinstance(f,dict) or not f.get('home') or not f.get('away'): continue
        out[(norm(f['home']),norm(f['away']),f.get('date',''))]=f
    return out

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

prelim=unique_fixtures(DATA.get('preliminary_fixtures') or {})
if len(prelim)<130:
    raise SystemExit(f'PRELIMINARY FIXTURE COVERAGE TOO LOW: {len(prelim)}')

# First Qualifying must remain permanently auditable even after the active fixture
# map advances. Before the first transition it is still the active map; afterwards
# auto_draw.py archives it in round_fixtures.
round_archive=DATA.get('round_fixtures') or {}
firstq_source=round_archive.get('First Round Qualifying')
if firstq_source is None and DATA.get('source_round')=='First Round Qualifying':
    firstq_source=DATA.get('fixtures') or {}
firstq=unique_fixtures(firstq_source or {})
if len(firstq)!=112:
    raise SystemExit(f'FIRST QUALIFYING FIXTURE COVERAGE IS NOT 112 TIES: {len(firstq)}')
for f in firstq.values():
    if f.get('conditional') or ' or ' in f.get('home','').lower() or ' or ' in f.get('away','').lower():
        raise SystemExit(f'UNRESOLVED FIRST QUALIFYING FIXTURE: {f.get("home")} v {f.get("away")}')

# The active map must agree with both its declared source_tie_count and the
# canonical Emirates FA Cup round size. This catches cross-competition ingestion
# and partial/full-draw parser failures before Clubfinder can rely on the data.
active=unique_fixtures(DATA.get('fixtures') or {})
active_round=DATA.get('source_round','')
declared=DATA.get('source_tie_count')
if declared is not None and len(active)!=int(declared):
    raise SystemExit(f'ACTIVE FIXTURE COVERAGE {len(active)} DOES NOT MATCH source_tie_count {declared}')
expected=EXPECTED_ACTIVE_TIES.get(active_round)
if expected is not None and len(active)!=expected:
    raise SystemExit(f'{active_round.upper()} FIXTURE COVERAGE IS NOT {expected} TIES: {len(active)}')
if not active:
    raise SystemExit('ACTIVE FIXTURE MAP IS EMPTY')

if 's.next.drawUrl' in HTML:
    raise SystemExit('BROKEN NEXT-ROUND LINK PROPERTY STILL PRESENT')
if "esc(k.round||next.name)" not in HTML:
    raise SystemExit('KNOWN FIXTURE ROUND LABEL DOES NOT USE LIVE FIXTURE ROUND')

print('COMPETITION REGRESSION GUARD: PASS')
print('Preliminary ties:',len(prelim))
print('First Qualifying ties preserved:',len(firstq))
print('Active round:',active_round)
print('Active ties:',len(active))
print('Canonical active-round tie count: PASS')
print('Representative chronology results: PASS')
