#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'clubfinder.html'; LEDGER=ROOT/'updater/ground-approval-ledger.json'; OUT=ROOT/'updater/critical-ground-batch5.json'; REPORT=ROOT/'critical-ground-batch5.md'
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
TARGETS=[
 {"name":"Liskeard Athletic FC","ground":"Lux Park","postcode":"PL14 3HZ","lat":50.460916,"lon":-4.46164,"source":"https://www.swpleague.co.uk/div-1-west/division-1-west/","ground_source":"Current league club directory; Lux Park independently confirmed","coordinate_source":"FCHD mapped Lux Park ground coordinate"},
 {"name":"Stockport Georgians FC","ground":"Cromley Road","postcode":"SK2 7DT","lat":53.3831,"lon":-2.1473,"source":"https://www.pitchero.com/clubs/stockportgeorgiansfc/contact","ground_source":"Current official club contact page","coordinate_source":"Open postcode/playing-field geodata for SK2 7DT; football playing field independently listed at address"},
 {"name":"SE Dons FC","ground":"The Bauvill Stadium","postcode":"ME4 6LR","lat":51.3686,"lon":0.5214,"source":"https://fulltime.thefa.com/displayTeam.html?divisionseason=261605801&teamID=80521829","ground_source":"FA Full-Time and current SCEFL evidence place SE Dons home matches at Bauvill Stadium","coordinate_source":"Mapped Chatham Town/Bauvill Stadium ground coordinate"},
]
REL=[
 {"tenant":"AFC Greenwich Borough","host":"Holmesdale FC","ground":"RTL Group Stadium","postcode":"BR2 8HQ","season":"2026-27","evidence":"AFC Greenwich Borough's current official site places its first team at RTL Group Stadium, 68 Oakley Road, while current club-history/directory evidence identifies the arrangement as a groundshare with Holmesdale FC.","source_url":"https://greenwichborough.com/"},
 {"tenant":"SE Dons FC","host":"Chatham Town FC","ground":"The Bauvill Stadium","postcode":"ME4 6LR","season":"2026-27","evidence":"Current SCEFL/FA Full-Time evidence places SE Dons home matches at the Bauvill Stadium and identifies the venue as a groundshare with Chatham Town.","source_url":"https://fulltime.thefa.com/displayTeam.html?divisionseason=261605801&teamID=80521829"},
]
PROTECTED={norm('Romulus FC'),norm('Sutton Coldfield Town FC')}
text=HTML.read_text(encoding='utf8'); gs,ge=locate(text,'GROUNDS'); grounds=json.loads(text[gs:ge]); es,ee=locate(text,'ELIGIBLE'); eligible=json.loads(text[es:ee])
elig={norm(x.get('name')):x.get('name') for x in eligible if x.get('name')}; by={}
for g in grounds: by.setdefault(norm(g.get('name') or g.get('club')),[]).append(g)
new=[]
for t in TARGETS:
 k=norm(t['name'])
 if k in PROTECTED: raise SystemExit('Protected club included.')
 if k not in elig: raise SystemExit(f"Safety stop: {t['name']} not eligible.")
 if by.get(k): raise SystemExit(f"Safety stop: existing canonical record for {t['name']}.")
 new.append({"name":elig[k],"ground":t['ground'],"postcode":t['postcode'],"lat":t['lat'],"lon":t['lon'],"verification":"verified","verification_label":"✅ Verified","source":"Current 2026/27 venue evidence: "+t['source'],"ground_source":t['ground_source'],"coordinate_source":t['coordinate_source']})
if len(new)!=3: raise SystemExit('Exactly three new records required.')
# Relationship safety: tenant and host must resolve exactly once at same postcode after additions.
combined=grounds+new; by2={}
for g in combined: by2.setdefault(norm(g.get('name') or g.get('club')),[]).append(g)
for r in REL:
 tr=by2.get(norm(r['tenant']),[]); hr=by2.get(norm(r['host']),[])
 if len(tr)!=1 or len(hr)!=1: raise SystemExit(f"Safety stop: relationship canonical resolution failed for {r['tenant']} -> {r['host']}.")
 if (tr[0].get('postcode') or '').upper()!=r['postcode'] or (hr[0].get('postcode') or '').upper()!=r['postcode']: raise SystemExit(f"Safety stop: postcode mismatch for {r['tenant']} -> {r['host']}.")
HTML.write_text(text[:gs]+json.dumps(grounds+sorted(new,key=lambda x:x['name'].lower()),ensure_ascii=False,separators=(',',':'))+text[ge:],encoding='utf8')
ledger=json.loads(LEDGER.read_text(encoding='utf8')); now=datetime.now(timezone.utc).isoformat(); known=ledger.get('known_groundshares') or []
for r in REL:
 entry={**r,"approved_at":now,"status":"current","approval_source":"v7.9.10 independently validated groundshare reconciliation"}
 known=[x for x in known if norm(x.get('tenant'))!=norm(r['tenant'])]+[entry]
ledger['known_groundshares']=known; ledger['version']='7.9.10'; ledger['updated_at']=now; LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
payload={"published_at":now,"version":"7.9.10","canonical_records_added":3,"existing_records_overwritten":0,"groundshares_recorded":2,"records":new,"relationships":REL,"protected_held":["Romulus FC","Sutton Coldfield Town FC"],"competition_json_changed":False}; OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
lines=['# Tin Foil FA Cup — Critical Ground Batch 5','',f'Published: **{datetime.now(timezone.utc).strftime("%d/%m/%Y, %H:%M:%S UTC")}**','','- New verified canonical records: **3**','- Existing records overwritten: **0**','- Current groundshares recorded: **2**','- Protected Romulus/Sutton Coldfield records changed: **0**','- `competition.json` changed: **NO**','','## Published records','']
for g in new: lines.append(f"- **{g['name']}** — {g['ground']} • {g['postcode']} • `{g['lat']}, {g['lon']}`")
lines += ['','## Current groundshares recorded','']
for r in REL: lines.append(f"- **{r['tenant']}** → {r['host']} • {r['ground']} • {r['postcode']} • {r['season']}")
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf8')
print('CRITICAL GROUND BATCH 5 v7.9.10'); print('New canonical records: 3'); print('Groundshares recorded: 2'); print('Existing records overwritten: 0'); print('Romulus/Sutton Coldfield: untouched')
