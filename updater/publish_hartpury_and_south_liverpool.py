#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'clubfinder.html'; LEDGER=ROOT/'updater/ground-approval-ledger.json'; OUT=ROOT/'updater/hartpury-south-liverpool-resolution.json'; REPORT=ROOT/'hartpury-south-liverpool-resolution.md'
def norm(s):
 s=(s or '').lower().replace('&',' and ').replace('’',"'"); s=re.sub(r'\b(fc|afc|cfc|football club)\b',' ',s); return re.sub(r'[^a-z0-9]+',' ',s).strip()
def locate(text,name):
 m=re.search(r'\b(?:const|let|var)\s+'+re.escape(name)+r'\s*=\s*\[',text)
 if not m: raise SystemExit('Could not find '+name)
 s=text.find('[',m.start()); d=0; ins=False; esc=False; q=''
 for i in range(s,len(text)):
  c=text[i]
  if ins:
   if esc: esc=False
   elif c=='\\': esc=True
   elif c==q: ins=False
  else:
   if c in ("'",'"'): ins=True;q=c
   elif c=='[': d+=1
   elif c==']':
    d-=1
    if d==0:return s,i+1
 raise SystemExit('Unbalanced '+name)
text=HTML.read_text(encoding='utf8'); gs,ge=locate(text,'GROUNDS'); grounds=json.loads(text[gs:ge]); es,ee=locate(text,'ELIGIBLE'); eligible=json.loads(text[es:ee])
elig={norm(x.get('name')):x.get('name') for x in eligible if x.get('name')}; by={}
for i,g in enumerate(grounds): by.setdefault(norm(g.get('name') or g.get('club')),[]).append((i,g))
protected={norm('Romulus FC'),norm('Sutton Coldfield Town FC')}
# Hartpury: add permanent/home canonical identity only. Temporary Gloucester fixtures are ledgered separately with dates.
hk=norm('Hartpury FC')
if hk not in elig: raise SystemExit('Safety stop: Hartpury FC no longer eligible.')
if by.get(hk): raise SystemExit('Safety stop: Hartpury canonical record already exists; no overwrite allowed.')
hartpury={"name":elig[hk],"ground":"4ED Hartpury Stadium, with Vodafone","postcode":"GL19 3BE","lat":51.90923,"lon":-2.30673,"verification":"verified","verification_label":"✅ Verified","source":"Current home-ground evidence: https://www.hartpury.ac.uk/hartpury-fc/getting-here/","ground_source":"Current official Hartpury FC getting-here page; permanent club home while pitch renovation is temporary","coordinate_source":"Hartpury University & College official sports map stadium marker"}
# South Liverpool: controlled verification-only correction. Ground/postcode/coordinates must already exist and are preserved.
sk=norm('South Liverpool FC'); sr=by.get(sk,[])
if len(sr)!=1: raise SystemExit(f'Safety stop: expected exactly one South Liverpool canonical record, found {len(sr)}.')
idx,south=sr[0]
if (south.get('ground') or '')!='Jericho Lane Sports Hub' or (south.get('postcode') or '').upper()!='L17 5AL': raise SystemExit('Safety stop: South Liverpool ground/postcode drift; research instead of overwriting.')
if south.get('lat') is None or south.get('lon') is None: raise SystemExit('Safety stop: South Liverpool existing coordinate missing.')
old_south=dict(south); south=dict(south); south['verification']='verified'; south['verification_label']='✅ Verified'; south['source']='Current 2026/27 venue evidence: https://www.southliverpoolfc.com/how-to-find-us/'; south['ground_source']='Current official South Liverpool site and NWCFL current club page confirm first team at Jericho Lane Sports Hub'; grounds[idx]=south
if norm(south.get('name') or south.get('club')) in protected: raise SystemExit('Protected club mutation attempted.')
grounds.append(hartpury); grounds.sort(key=lambda x:(x.get('name') or x.get('club') or '').lower())
HTML.write_text(text[:gs]+json.dumps(grounds,ensure_ascii=False,separators=(',',':'))+text[ge:],encoding='utf8')
# Preserve ledger schema; add a distinct time-bounded field so temporary venue use is never confused with a permanent known_groundshare.
ledger=json.loads(LEDGER.read_text(encoding='utf8')); now=datetime.now(timezone.utc).isoformat(); temps=ledger.get('temporary_groundshares') or []
temp={"tenant":"Hartpury FC","host":"Gloucester City AFC","ground":"The KMM Energy Stadium","postcode":"GL2 5HD","season":"2026-27","effective_from":"2026-08-29","effective_through":"2026-10-03","affected_home_fixtures":["2026-08-29 Exmouth Town (FA Trophy)","2026-09-15 Melksham Town","2026-09-22 Worcester Raiders","2026-09-26 Bideford AFC","2026-10-03 Barnstaple Town"],"status":"temporary","evidence":"Southern League and Gloucester City independently confirm Hartpury will use Gloucester City's KMM Energy Stadium only for these five home fixtures while 3G works are completed at 4ED Hartpury Stadium.","source_url":"https://www.southern-football-league.co.uk/articles/hartpury-fc-announce-temporary-groundshare-agreement-at-the-kmm-energy-stadium","recorded_at":now,"approval_source":"v7.9.12 time-bounded venue handling"}
temps=[x for x in temps if not (norm(x.get('tenant'))==norm('Hartpury FC') and x.get('season')=='2026-27')]+[temp]; ledger['temporary_groundshares']=temps; ledger['version']='7.9.12'; ledger['updated_at']=now; LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
payload={"published_at":now,"version":"7.9.12","hartpury_canonical_added":1,"south_liverpool_verified":1,"existing_ground_or_postcode_overwritten":0,"temporary_groundshares_recorded":1,"protected_relationship_changed":0,"hartpury":hartpury,"south_liverpool_before":{"ground":old_south.get('ground'),"postcode":old_south.get('postcode'),"verification":old_south.get('verification')},"south_liverpool_after":{"ground":south.get('ground'),"postcode":south.get('postcode'),"verification":south.get('verification')},"temporary":temp,"competition_json_changed":False}; OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
lines=['# Tin Foil FA Cup — Hartpury / South Liverpool Resolution','',f'Published: **{datetime.now(timezone.utc).strftime("%d/%m/%Y, %H:%M:%S UTC")}**','','- Hartpury permanent/home canonical record added: **1**','- South Liverpool existing record promoted from unverified to verified: **1**','- South Liverpool ground/postcode/coordinates changed: **NO**','- Time-bounded Hartpury temporary groundshare recorded: **1**','- Romulus/Sutton Coldfield changed: **NO**','- `competition.json` changed: **NO**','','## Hartpury FC','','- Canonical home: **4ED Hartpury Stadium, with Vodafone • GL19 3BE**','- Temporary venue: **KMM Energy Stadium • GL2 5HD**','- Effective temporary period: **29 August 2026 through 3 October 2026**','- Only the five explicitly announced affected home fixtures are included.','','## South Liverpool FC','','- **Jericho Lane Sports Hub • L17 5AL** retained unchanged.','- Verification upgraded to **verified** from current official club and league evidence.','','## Safety','','- A temporary groundshare is stored separately from permanent `known_groundshares`.','- Hartpury is not permanently moved to Gloucester.','- South Liverpool ground/postcode/coordinates are not rewritten.','- Romulus FC and Sutton Coldfield Town FC remain untouched.']
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf8')
print('HARTPURY / SOUTH LIVERPOOL RESOLUTION v7.9.12'); print('Hartpury canonical: added'); print('South Liverpool: verification only'); print('Temporary Hartpury venue: time-bounded'); print('Romulus/Sutton Coldfield: untouched')
