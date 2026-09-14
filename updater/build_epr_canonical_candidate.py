#!/usr/bin/env python3
"""Build a review-only canonical EPR candidate from exact FWP matches.

Only source rows that match a legacy protected tie by teams/orientation/score are
included. Ambiguous walkover/status cases are excluded and listed separately.
No production data is modified.
"""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'clubfinder.html').read_text(encoding='utf-8')
SRC=json.loads((ROOT/'epr-authoritative-source-audit.json').read_text(encoding='utf-8'))
OUT=ROOT/'epr-canonical-candidate.json'
MD=ROOT/'epr-canonical-candidate.md'
ALIASES={
 'atherton lr':'atherton laburnum rovers','irlam':'irlam town','eastwood community':'eastwood cfc',
 'bedfont sports club':'bedfont sports','royal wootton bassett town':'royal wootton bassett',
 'varndeanians':'varndenians','sherborne town':'sherbourne town','bournemouth poppies':'bournemouth'
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
    if depth==0:return json.loads(HTML[i:j+1])
 raise SystemExit('unbalanced object')

def norm(v):
 s=str(v or '').lower().replace('&',' and ')
 s=re.sub(r'\([^)]*\)',' ',s); s=re.sub(r'\b(afc|fc)\b',' ',s); s=s.replace('town 88','town')
 s=' '.join(re.sub(r'[^a-z0-9]+',' ',s).split())
 return ALIASES.get(s,s)

def num(v):
 try:return int(v)
 except:return None

def winner(home,hs,away,as_):
 if hs is None or as_ is None or hs==as_: return None
 return home if hs>as_ else away

source=[]
for page in SRC.get('pages',[]):
 for table in page.get('tables',[]):
  for row in table.get('rows',[]):
   if len(row)<6:continue
   d,status,home,hs,as_,away=row[:6]
   if not re.search(r'\d/\d/2026',str(d or '')):continue
   source.append({'date':page['date'],'round':page['expected_round'],'source_url':page['url'],'status':status,
                  'home':home,'home_score':num(hs),'away_score':num(as_),'away':away,'nh':norm(home),'na':norm(away)})

legacy=extract('EPR_RESULTS_BY_TIE')
candidate=[]; excluded=[]
for key,r in legacy.items():
 if not isinstance(r,dict) or not all(x in r for x in ('home','away','home_score','away_score')):continue
 nh,na=norm(r.get('home')),norm(r.get('away')); hs,as_=num(r.get('home_score')),num(r.get('away_score'))
 hits=[s for s in source if s['nh']==nh and s['na']==na and s['home_score']==hs and s['away_score']==as_]
 if len(hits)==1:
  s=hits[0]
  candidate.append({'legacy_tie_id':str(key),'round':s['round'],'date':s['date'],'home':s['home'],'away':s['away'],
                    'home_score':s['home_score'],'away_score':s['away_score'],'winner':winner(s['home'],s['home_score'],s['away'],s['away_score']),
                    'status':s['status'],'source_url':s['source_url'],'legacy_decision':r.get('decision') or ''})
 else:
  excluded.append({'legacy_tie_id':str(key),'legacy':r,'matching_source_rows':hits})

payload={'schema':'review-only-epr-canonical-candidate-v1','source':'Football Web Pages','candidate_rows':candidate,'excluded_rows':excluded}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
lines=['# Extra Preliminary canonical candidate','', 'REVIEW ONLY. Production data unchanged.','',
       f'- Source-exact candidate rows: **{len(candidate)}**',f'- Excluded / unresolved legacy rows: **{len(excluded)}**','',
       'Winners are derived from decisive FWP scorelines only. Drawn scorelines are intentionally left without a winner here; legacy decision text is retained as review metadata, not treated as source proof.','',
       '## Excluded rows','']
for x in excluded:
 r=x['legacy']; lines.append(f'- Tie {x["legacy_tie_id"]}: {r.get("home")} {r.get("home_score")}-{r.get("away_score")} {r.get("away")}; decision={r.get("decision")!r}; winner={r.get("winner")!r}')
MD.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('EPR CANONICAL CANDIDATE BUILT')
print('candidate',len(candidate)); print('excluded',len(excluded)); print('REVIEW ONLY. Production main untouched.')
