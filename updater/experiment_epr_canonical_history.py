#!/usr/bin/env python3
"""Disposable experiment: migrate sourced EPR outcomes into competition.result_history
and blank the legacy EPR_RESULTS_BY_TIE table in the working copy.

This script is intentionally branch/CI-only. It changes competition.json and
clubfinder.html in the checkout so regressions can prove behaviour equivalence.
It does not itself commit either production file.
"""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
COMP=ROOT/'competition.json'
HTML=ROOT/'clubfinder.html'
CAND=ROOT/'epr-canonical-candidate.json'
REPORT=ROOT/'epr-canonical-history-experiment.md'

data=json.loads(COMP.read_text(encoding='utf-8'))
cand=json.loads(CAND.read_text(encoding='utf-8'))
rows=cand.get('candidate_rows') or []
excluded=cand.get('excluded_rows') or []
if len(rows)!=218 or excluded:
    raise SystemExit(f'ABORT: expected 218 sourced rows and 0 excluded; got {len(rows)} / {len(excluded)}')

rh=data.setdefault('result_history',{})
original_keys=len(rh)
appended=0
created_keys=0

def short_name(name):
    return re.sub(r'\s+(FC|AFC|CFC)$','',str(name or ''),flags=re.I).strip()

def semantic_key(r):
    return (
        str(r.get('round') or ''),str(r.get('date') or ''),
        short_name(r.get('home')).lower(),short_name(r.get('away')).lower(),
        r.get('home_score'),r.get('away_score'),str(r.get('decision') or '').lower(),
        short_name(r.get('winner')).lower()
    )

# Explicit aliases bridge source display names to Clubfinder origin names where
# known naming differs. Keys are aliases only; result payload remains sourced.
ALIASES={
    'Newton Aycliffe':['Newton Aycliffe FC'],
    'Kendal Town':['Kendal Town FC'],
    'Marske United':['Marske United FC'],
    'Abbey Hulton United':['Abbey Hulton United FC'],
    'Kidsgrove Athletic':['Kidsgrove Athletic FC'],
    'Boro Rangers':['Boro Rangers FC'],
    'AFC Varndenians':['AFC Varndeanians','AFC Varndeanians FC'],
    'Atherton Laburnum Rovers':['Atherton LR'],
    'Eastwood CFC':['Eastwood Community','Eastwood Community FC'],
    'Irlam Town':['Irlam','Irlam FC'],
    'Royal Wootton Bassett':['Royal Wootton Bassett Town','Royal Wootton Bassett Town FC'],
    'Sherbourne Town':['Sherborne Town','Sherborne Town FC'],
    'Bournemouth FC':['Bournemouth Poppies','Bournemouth Poppies FC'],
    'Bedfont Sports':['Bedfont Sports Club','Bedfont Sports Club FC'],
}

def keys_for_team(name):
    vals=[str(name),short_name(name)]
    vals += ALIASES.get(str(name),[])
    vals += ALIASES.get(short_name(name),[])
    out=[]
    for v in vals:
        v=str(v).strip()
        if v and v not in out: out.append(v)
    return out

for src in rows:
    r={k:src.get(k) for k in ('round','date','home','away','home_score','away_score','winner','status','decision','source_url')}
    # Keep administrative walkovers scoreless. Do not invent a played match.
    if str(r.get('decision') or '').lower()=='walkover':
        r['home_score']=None; r['away_score']=None
    for team in (r.get('home'),r.get('away')):
        for key in keys_for_team(team):
            arr=rh.get(key)
            if arr is None:
                arr=[]; rh[key]=arr; created_keys+=1
            if not isinstance(arr,list):
                raise SystemExit(f'ABORT: result_history[{key!r}] is not a list')
            sk=semantic_key(r)
            if not any(semantic_key(x)==sk for x in arr if isinstance(x,dict)):
                arr.append(dict(r)); appended+=1
                arr.sort(key=lambda x:(str(x.get('date') or ''),str(x.get('round') or '')))

COMP.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

text=HTML.read_text(encoding='utf-8')
m=re.search(r'\bconst\s+EPR_RESULTS_BY_TIE\s*=\s*\{',text)
if not m: raise SystemExit('ABORT: EPR_RESULTS_BY_TIE assignment not found')
start=m.end()-1
depth=0; quote=None; esc=False; end=None
for i in range(start,len(text)):
    ch=text[i]
    if quote:
        if esc: esc=False
        elif ch=='\\': esc=True
        elif ch==quote: quote=None
    else:
        if ch in "'\"`": quote=ch
        elif ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:
                end=i+1; break
if end is None: raise SystemExit('ABORT: EPR_RESULTS_BY_TIE object not balanced')
removed=end-start-2
text=text[:start]+'{}'+text[end:]
HTML.write_text(text,encoding='utf-8')

# Useful proof points before the JS regressions run.
new=json.loads(COMP.read_text(encoding='utf-8'))['result_history']
def find(team,home,away,hs,as_):
    arr=new.get(team,[])
    return any(short_name(x.get('home')).lower()==short_name(home).lower() and short_name(x.get('away')).lower()==short_name(away).lower() and x.get('home_score')==hs and x.get('away_score')==as_ for x in arr)
checks={
 'Newton Aycliffe canonical EPR':find('Newton Aycliffe FC','Newton Aycliffe','Kendal Town',0,1),
 'Marske administrative bye':any((x.get('decision')=='walkover' and short_name(x.get('winner')).lower()=='marske united') for x in new.get('Marske United FC',[])),
 'Abbey Hulton administrative award':any((x.get('decision')=='walkover' and short_name(x.get('winner')).lower()=='abbey hulton united') for x in new.get('Abbey Hulton United FC',[])),
}
for label,ok in checks.items():
    if not ok: raise SystemExit('ABORT: '+label+' missing after migration')

REPORT.write_text('\n'.join([
 '# Disposable EPR canonical-history experiment','',
 'Production main unchanged. Working-copy mutation only.','',
 f'- Candidate rows migrated: **{len(rows)}**',
 f'- Existing result_history keys before migration: **{original_keys}**',
 f'- New result_history keys created: **{created_keys}**',
 f'- History records appended across lookup aliases: **{appended}**',
 f'- Legacy EPR table payload removed from working copy: **{removed} bytes**','',
 'Proof points before regressions:','',
 *[f'- {k}: **PASS**' for k,v in checks.items() if v],''
 ])+'\n',encoding='utf-8')
print('EPR CANONICAL HISTORY EXPERIMENT: PREPARED')
print('candidate rows:',len(rows))
print('new result_history keys:',created_keys)
print('history records appended:',appended)
print('legacy EPR bytes removed:',removed)
print('Production main untouched.')
