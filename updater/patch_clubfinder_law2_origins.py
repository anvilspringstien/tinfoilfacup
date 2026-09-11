#!/usr/bin/env python3
"""Guarded 491 -> 651 Law 2 origin expansion for Clubfinder v7.6."""
from pathlib import Path
import json,re,urllib.request
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'clubfinder.html'; REGISTRY=ROOT/'journey-club-registry.json'
NEW={'First Round Qualifying','Second Round Qualifying','Fourth Round Qualifying'}
ALL={'Extra Preliminary Round','Preliminary Round',*NEW}
# The protected v7.6 data currently carries a 437/54 split across its first two
# entry labels. This patch deliberately does not rewrite those protected 491
# records; it adds the 160 later qualifying entrants only. The separate FA
# reconciliation remains responsible for any legacy entry-label correction.
EXPECTED={'Extra Preliminary Round':437,'Preliminary Round':54,'First Round Qualifying':88,'Second Round Qualifying':48,'Fourth Round Qualifying':24}
# Explicit current-club evidence overrides stale supporting-gazetteer records.
# Warrington Rylands' official club pages give WA2 7RZ for the Quickline
# Logistics Arena; the companion FCHD candidate currently contains WA3 7RZ.
LOCATION_OVERRIDES={
 'warrington rylands':{
  'ground':'The Quickline Logistics Arena',
  'postcode':'WA2 7RZ',
  'source':'https://warringtonrylandsfc.co.uk/arena',
  'ground_source':'Official Warrington Rylands current arena page',
 }
}
def norm(s):
 s=str(s or '').lower().replace('&',' and ');s=re.sub(r'\b(fc|afc|cfc)\b',' ',s);return re.sub(r'[^a-z0-9]+',' ',s).strip()
def locate(t,n):
 m=re.search(r'\b(?:const|let|var)\s+'+re.escape(n)+r'\s*=\s*\[',t)
 if not m:return None
 s=t.find('[',m.start());d=0;ins=False;esc=False;q=''
 for i in range(s,len(t)):
  c=t[i]
  if ins:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==q:ins=False
  else:
   if c in ('"',"'"):ins=True;q=c
   elif c=='[':d+=1
   elif c==']':
    d-=1
    if d==0:return s,i+1
 raise SystemExit(f'ABORT: unbalanced {n}')
def arr(t,n):
 p=locate(t,n)
 if not p:raise SystemExit(f'ABORT: {n} missing')
 return json.loads(t[p[0]:p[1]]),p[0],p[1]
def compact(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
def geocode(postcodes):
 pcs=sorted({str(x).strip().upper() for x in postcodes if x});out={}
 for i in range(0,len(pcs),100):
  chunk=pcs[i:i+100];body=json.dumps({'postcodes':chunk}).encode();req=urllib.request.Request('https://api.postcodes.io/postcodes',data=body,headers={'Content-Type':'application/json','User-Agent':'TinFoilFACup-Law2/1.0'},method='POST')
  try:
   with urllib.request.urlopen(req,timeout=30) as r:data=json.loads(r.read().decode())
  except Exception as e:raise SystemExit(f'ABORT: Postcodes.io bulk geocode failed: {e}')
  for x in data.get('result') or []:
   res=x.get('result') or {};pc=str(x.get('query') or '').upper()
   if res.get('latitude') is not None and res.get('longitude') is not None:out[pc]=(float(res['latitude']),float(res['longitude']))
 miss=[x for x in pcs if x not in out]
 if miss:raise SystemExit('ABORT: no coordinates for '+', '.join(miss))
 return out
text=HTML.read_text(encoding='utf-8');reg=json.loads(REGISTRY.read_text(encoding='utf-8'));selected=[x for x in reg.get('clubs',[]) if x.get('entry_round') in NEW]
if len(selected)!=160:raise SystemExit(f'ABORT: expected 160 additional Law 2 clubs, found {len(selected)}')
elig,es,ee=arr(text,'ELIGIBLE');grounds,_,_=arr(text,'GROUNDS')
if len({norm(x.get('name')) for x in elig})!=len(elig):raise SystemExit('ABORT: duplicate ELIGIBLE identity')
by={norm(x.get('name')):x for x in elig};gby={norm(x.get('name') or x.get('club')):x for x in grounds}
for x in selected:
 k=norm(x['club'])
 if k not in by:
  rec={'name':x['club'],'entry_round':x['entry_round'],'fixture':{}};elig.append(rec);by[k]=rec
 else:by[k]['entry_round']=x['entry_round']
if len(elig)!=651:raise SystemExit(f'ABORT: expected 651 Law 2 origins, found {len(elig)}')
counts={}
for c in elig:
 r=c.get('entry_round');counts[r]=counts.get(r,0)+1
 if r not in ALL:raise SystemExit(f"ABORT: non-Law-2 origin {c.get('name')} — {r}")
if counts!=EXPECTED:raise SystemExit(f'ABORT: Law 2 entry-round cohort drift: {counts}')
old=[];p=locate(text,'LAW2_ORIGIN_LOCATIONS')
if p:old=json.loads(text[p[0]:p[1]])
oldby={norm(x.get('name')):x for x in old};support=[];need=[]
for x in selected:
 k=norm(x['club'])
 if k in gby:continue
 override=LOCATION_OVERRIDES.get(k)
 if override:
  e=override
 else:
  ev=[e for e in (x.get('supporting_ground_evidence') or []) if e.get('ground') and e.get('postcode')]
  if len(ev)!=1:raise SystemExit(f"ABORT: {x['club']} has {len(ev)} usable supporting home-ground candidates")
  e=ev[0]
 pc=str(e['postcode']).strip().upper();o=oldby.get(k) or {};r={'name':x['club'],'ground':e['ground'],'postcode':pc,'verification':'supporting-evidence','verification_label':'⚠️ Unverified','source':e.get('source') or 'FCHD gazetteer candidate evidence','ground_source':e.get('ground_source') or 'Law 2 supporting home-ground evidence; not automatically verified','law2_origin_location':True}
 if o.get('postcode')==pc and o.get('lat') is not None and o.get('lon') is not None:r.update(lat=float(o['lat']),lon=float(o['lon']),coordinate_source=o.get('coordinate_source') or 'Postcodes.io postcode centroid')
 else:need.append(pc)
 support.append(r)
if need:
 geo=geocode(need)
 for r in support:
  if r.get('lat') is None:r['lat'],r['lon']=geo[r['postcode']];r['coordinate_source']='Postcodes.io postcode centroid'
text=text[:es]+compact(elig)+text[ee:]
_,_,ge=arr(text,'GROUNDS');decl='const LAW2_ORIGIN_LOCATIONS='+compact(support)+';';p=locate(text,'LAW2_ORIGIN_LOCATIONS')
if p:
 m=re.search(r'\bconst\s+LAW2_ORIGIN_LOCATIONS\s*=\s*\[',text);semi=text.find(';',p[1]);text=text[:m.start()]+decl+text[semi+1:]
else:
 semi=text.find(';',ge);text=text[:semi+1]+decl+text[semi+1:]
oldfind="""function findGround(c){
  const candidates=[c.name,aliases[c.name],c.name.replace(/ FC$/,'').replace(/ AFC$/,'').replace(/ CFC$/,'')].filter(Boolean);
  for(const candidate of candidates){
    const n=norm(candidate);
    const g=GROUNDS.find(x=>norm(x.name)===n);
    if(g)return g;
  }
  return null
}"""
newfind="""function findGround(c){
  const candidates=[c.name,aliases[c.name],c.name.replace(/ FC$/,'').replace(/ AFC$/,'').replace(/ CFC$/,'')].filter(Boolean);
  for(const candidate of candidates){
    const n=norm(candidate);
    const g=GROUNDS.find(x=>norm(x.name)===n);
    if(g)return g;
    const s=LAW2_ORIGIN_LOCATIONS.find(x=>norm(x.name)===n);
    if(s)return s;
  }
  return null
}"""
if oldfind in text:text=text.replace(oldfind,newfind,1)
elif newfind not in text:raise SystemExit('ABORT: findGround boundary changed')
oldgb="""  const g=GROUNDS.find(g=>canonicalClubKey(g.name||g.club)===target);
  if(g)return g;
  const c=ELIGIBLE.find(c=>canonicalClubKey(c.name)===target);"""
newgb="""  const g=GROUNDS.find(g=>canonicalClubKey(g.name||g.club)===target);
  if(g)return g;
  const s=LAW2_ORIGIN_LOCATIONS.find(g=>canonicalClubKey(g.name||g.club)===target);
  if(s)return s;
  const c=ELIGIBLE.find(c=>canonicalClubKey(c.name)===target);"""
if oldgb in text:text=text.replace(oldgb,newgb,1)
elif newgb not in text:raise SystemExit('ABORT: groundByClubName boundary changed')
oldprev="""  let body='<div class=\"history\"><div class=\"history-title\">Previous Rounds</div>'+\n    '<div class=\"history-origin\">Journey started with: '+esc(journey.origin.name)+'</div>';\n\n  if(!crumbs.length){"""
newprev="""  let body='<div class=\"history\"><div class=\"history-title\">Previous Rounds</div>'+\n    '<div class=\"history-origin\">Journey started with: '+esc(journey.origin.name)+'</div>';\n  const entryRound=journey.origin.entry_round||'';\n  if(entryRound&&entryRound!=='Extra Preliminary Round'){\n    body+='<div class=\"history-entry\">'+esc(journey.origin.name)+' enters the competition at '+esc(entryRound)+'.</div>';\n  }\n\n  if(!crumbs.length){"""
if oldprev in text:text=text.replace(oldprev,newprev,1)
elif newprev not in text:raise SystemExit('ABORT: previousRoundsHtml boundary changed')
if 'const top=rows.slice(0,3);' not in text:raise SystemExit('ABORT: nearest-three selector changed')
for marker in ('const LAW2_ORIGIN_LOCATIONS=','LAW2_ORIGIN_LOCATIONS.find',"enters the competition at '+esc(entryRound)+'."):
 if marker not in text:raise SystemExit('ABORT: Law 2 marker missing: '+marker)
HTML.write_text(text,encoding='utf-8')
print('CLUBFINDER LAW 2 ORIGIN EXPANSION: SUCCESS');print('Selectable Law 2 origins:',len(elig));print('Entry rounds:',counts);print('Additional qualifying origins:',len(selected));print('Supplemental supporting home-ground locations:',len(support));print('Protected GROUNDS array: UNTOUCHED');print('Nearest journeys returned: 3');print('Proper-round-only origins: EXCLUDED')
