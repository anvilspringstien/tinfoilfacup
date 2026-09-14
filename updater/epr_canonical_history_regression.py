#!/usr/bin/env python3
from pathlib import Path
import json,re,sys

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'clubfinder.html').read_text(encoding='utf-8')
data=json.loads((ROOT/'competition.json').read_text(encoding='utf-8'))
rh=data.get('result_history',{})

m=re.search(r'\bconst\s+EPR_RESULTS_BY_TIE\s*=\s*(\{.*?\})\s*;',html,re.S)
if not m:
    raise SystemExit('FAIL: EPR_RESULTS_BY_TIE assignment missing')
if m.group(1).strip()!='{}':
    raise SystemExit('FAIL: legacy EPR_RESULTS_BY_TIE is not blank')

def short(v):
    return re.sub(r'\s+(FC|AFC|CFC)$','',str(v or ''),flags=re.I).strip().lower()

def has(team,home,away,hs,as_,winner=None,decision=None):
    for r in rh.get(team,[]):
        if short(r.get('home'))!=short(home) or short(r.get('away'))!=short(away): continue
        if r.get('home_score')!=hs or r.get('away_score')!=as_: continue
        if winner is not None and short(r.get('winner'))!=short(winner): continue
        if decision is not None and str(r.get('decision') or '')!=decision: continue
        return True
    return False

checks=[
 ('Newton Aycliffe 0-1 Kendal canonical history',has('Newton Aycliffe FC','Newton Aycliffe','Kendal Town',0,1,'Kendal Town')),
 ('Marske bye canonical history',has('Marske United FC','Marske United','Boro Rangers',None,None,'Marske United','walkover')),
 ('Abbey Hulton awarded replay canonical history',has('Abbey Hulton United FC','Abbey Hulton United','Kidsgrove Athletic',None,None,'Abbey Hulton United','walkover')),
]
for label,ok in checks:
    if not ok: raise SystemExit('FAIL: '+label)

# Pigeon Miles helper must continue to exclude administrative walkovers.
if "decision||'').toLowerCase()!=='walkover'" not in html:
    raise SystemExit('FAIL: Pigeon Miles walkover exclusion guard missing')

print('EPR CANONICAL HISTORY REGRESSION: PASS')
for label,_ in checks: print(label,'— PASS')
print('Legacy EPR_RESULTS_BY_TIE blank — PASS')
print('Pigeon Miles walkover exclusion guard — PASS')
