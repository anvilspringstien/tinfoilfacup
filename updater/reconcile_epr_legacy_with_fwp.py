#!/usr/bin/env python3
"""Reconcile legacy EPR_RESULTS_BY_TIE against Football Web Pages source rows.

Read-only. Produces a classification report showing which legacy rows map cleanly
to actual dated ties/replays and which require naming/status review before any
canonical migration.
"""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'clubfinder.html').read_text(encoding='utf-8')
SRC=json.loads((ROOT/'epr-authoritative-source-audit.json').read_text(encoding='utf-8'))
OUT=ROOT/'epr-legacy-reconciliation.md'

ALIASES={
    'atherton lr':'atherton laburnum rovers',
    'irlam':'irlam town',
    'eastwood community':'eastwood cfc',
    'bedfont sports club':'bedfont sports',
    'royal wootton bassett town':'royal wootton bassett',
    'afc varndeanians':'afc varndenians',
    'sherborne town':'sherbourne town',
    'bournemouth poppies':'bournemouth',
}


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
    s=re.sub(r'\([^)]*\)',' ',s)
    s=re.sub(r'\b(afc|fc)\b',' ',s)
    s=s.replace('town 88','town')
    s=' '.join(re.sub(r'[^a-z0-9]+',' ',s).split())
    return ALIASES.get(s,s)


def score(v):
    try:return int(v)
    except:return None

legacy=extract('EPR_RESULTS_BY_TIE')
source=[]
for page in SRC.get('pages',[]):
    for table in page.get('tables',[]):
        cols=table.get('columns',[])
        if cols[:6]!=['Date','Status','Home','Score','Score.1','Away']: continue
        for row in table.get('rows',[]):
            if len(row)<6: continue
            d,status,home,hs,as_,away=row[:6]
            if not re.search(r'\d/\d/2026',str(d or '')): continue
            source.append({
                'date':page['date'],'round':page['expected_round'],'source_url':page['url'],
                'status':status,'home':home,'home_score':score(hs),'away_score':score(as_),'away':away,
                'nh':norm(home),'na':norm(away)
            })

cats={'exact':[],'swapped':[],'pair_only':[],'unmatched':[]}
for key,r in legacy.items():
    if not isinstance(r,dict) or not all(x in r for x in ('home','away','home_score','away_score')): continue
    nh,na=norm(r.get('home')),norm(r.get('away'))
    hs,as_=score(r.get('home_score')),score(r.get('away_score'))
    exact=[s for s in source if s['nh']==nh and s['na']==na and s['home_score']==hs and s['away_score']==as_]
    swapped=[s for s in source if s['nh']==na and s['na']==nh and s['home_score']==as_ and s['away_score']==hs]
    pair=[s for s in source if {s['nh'],s['na']}=={nh,na}]
    item=(str(key),r,exact or swapped or pair)
    if exact: cats['exact'].append(item)
    elif swapped: cats['swapped'].append(item)
    elif pair: cats['pair_only'].append(item)
    else: cats['unmatched'].append(item)

lines=['# Extra Preliminary legacy reconciliation','',
       'READ ONLY. No production data changed.','',
       f'- Legacy rows inspected: **{sum(len(v) for v in cats.values())}**',
       f'- Football Web Pages dated rows available: **{len(source)}**',
       f'- Exact same orientation + score matches after known club-alias normalisation: **{len(cats["exact"])}**',
       f'- Exact score/team matches with home/away reversed: **{len(cats["swapped"])}**',
       f'- Team-pair matches but score/status differs: **{len(cats["pair_only"])}**',
       f'- No source pair found in audited dates: **{len(cats["unmatched"])}**','']

lines += ['## Alias normalisation used','']
for a,b in sorted(ALIASES.items()): lines.append(f'- `{a}` → `{b}`')
lines.append('')

for cat,title in [('swapped','Orientation differences'),('pair_only','Same clubs, different recorded score/status'),('unmatched','Unmatched legacy rows')]:
    lines += [f'## {title}','']
    if not cats[cat]: lines += ['None.','']; continue
    for key,r,cands in cats[cat]:
        lines.append(f'- Tie {key}: **{r.get("home")} {r.get("home_score")}-{r.get("away_score")} {r.get("away")}**; legacy decision=`{r.get("decision","")}`; legacy winner=`{r.get("winner","")}`')
        for s in cands[:6]:
            lines.append(f'  - FWP {s["date"]} {s["round"]}: {s["home"]} {s["home_score"]}-{s["away_score"]} {s["away"]}; status={s["status"]}; source={s["source_url"]}')
    lines.append('')

lines += ['## Migration rule','',
          'Only exact dated source matches should be auto-promoted. Known club-name aliases above are identity normalisation only, not score/result overrides. Pair-only and unmatched rows remain fail-closed for manual review.','']
OUT.write_text('\n'.join(lines),encoding='utf-8')
print('EPR LEGACY RECONCILIATION COMPLETE')
for k,v in cats.items(): print(k,len(v))
print('READ ONLY. Production main untouched.')
