#!/usr/bin/env python3
"""Read-only audit of legacy EPR_RESULTS_BY_TIE for safe canonical migration.

Checks whether the table can be copied as result records, or whether winner/draw
semantics need normalisation first. No production data is changed.
"""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'clubfinder.html').read_text(encoding='utf-8')

def extract(name):
    m=re.search(r'\bconst\s+'+re.escape(name)+r'\s*=',HTML)
    if not m: raise SystemExit(f'{name} not found')
    i=m.end()
    while HTML[i].isspace(): i+=1
    depth=0; quote=None; esc=False
    for j in range(i,len(HTML)):
        ch=HTML[j]
        if quote:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: quote=None
        else:
            if ch in "'\"`": quote=ch
            elif ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0: return json.loads(HTML[i:j+1])
    raise SystemExit('unbalanced object')

def norm(v):
    s=str(v or '').lower().replace('&',' and ')
    s=re.sub(r'\b(afc|fc)\b',' ',s)
    return ' '.join(re.sub(r'[^a-z0-9]+',' ',s).split())

def rows(obj):
    out=[]
    for k,v in obj.items():
        if isinstance(v,dict) and all(x in v for x in ('home','away','home_score','away_score')):
            out.append((str(k),v))
    return out

data=rows(extract('EPR_RESULTS_BY_TIE'))
fields={}
draws=[]; decisive=[]; inconsistent=[]; missing_winner=[]; dates={}; sources=0; decisions={}
for key,r in data:
    for f in r: fields[f]=fields.get(f,0)+1
    dates[str(r.get('date'))]=dates.get(str(r.get('date')),0)+1
    if r.get('source_url'): sources+=1
    decisions[str(r.get('decision') or '')]=decisions.get(str(r.get('decision') or ''),0)+1
    hs,as_=int(r['home_score']),int(r['away_score'])
    w=r.get('winner')
    if hs==as_:
        draws.append((key,r))
    else:
        decisive.append((key,r))
        expected=r['home'] if hs>as_ else r['away']
        if not w: missing_winner.append((key,r,expected))
        elif norm(w)!=norm(expected): inconsistent.append((key,r,expected))

print('EPR MIGRATION READINESS AUDIT')
print('Rows:',len(data))
print('Decisive scorelines:',len(decisive))
print('Drawn scorelines:',len(draws))
print('Decisive rows whose winner field conflicts with scoreline:',len(inconsistent))
print('Decisive rows missing winner field:',len(missing_winner))
print('Rows with source_url:',sources)
print('Dates:',json.dumps(dates,sort_keys=True))
print('Decision values:',json.dumps(decisions,sort_keys=True))
print('Field coverage:',json.dumps(fields,sort_keys=True))

if inconsistent:
    print('\nWINNER CONFLICTS (first 50):')
    for key,r,expected in inconsistent[:50]:
        print(f'- tie {key}: {r["home"]} {r["home_score"]}-{r["away_score"]} {r["away"]}; stored winner={r.get("winner")!r}; scoreline winner={expected!r}')

if draws:
    print('\nDRAWS / REPLAY-SEMANTICS CANDIDATES (first 50):')
    for key,r in draws[:50]:
        print(f'- tie {key}: {r["home"]} {r["home_score"]}-{r["away_score"]} {r["away"]}; stored winner={r.get("winner")!r}; date={r.get("date")}; decision={r.get("decision")!r}')

print('\nMIGRATION VERDICT:')
if inconsistent or draws or sources < len(data):
    print('NOT SAFE TO COPY BLINDLY into canonical competition results.')
    if inconsistent: print('- Winner semantics must be normalised from decisive scorelines.')
    if draws: print('- Drawn ties need replay chronology/decision handling rather than an invented winner.')
    if sources < len(data): print('- Source provenance is incomplete in the legacy table.')
else:
    print('Structurally clean for canonical migration, subject to provenance review.')
print('READ ONLY. Production main untouched.')
