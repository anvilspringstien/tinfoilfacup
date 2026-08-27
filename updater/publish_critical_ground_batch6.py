#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'clubfinder.html'; OUT=ROOT/'updater/critical-ground-batch6.json'; REPORT=ROOT/'critical-ground-batch6.md'
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
 {"name":"Fleetlands FC","ground":"Powder Monkey Park","postcode":"PO13 0AX","lat":50.833547,"lon":-1.171164,"source":"https://www.wessexleague.co.uk/premier-division","ground_source":"Current Wessex League 2026/27 Premier Division club directory and current Fleetlands site","coordinate_source":"FCHD mapped Powder Monkey Park ground coordinate"},
 {"name":"Sutton United FC (Birmingham)","ground":"Coleshill Road Stadium","postcode":"B75 7BA","lat":52.55959,"lon":-1.813718,"source":"https://suttonunitedfc.co.uk/","ground_source":"Current official Sutton United first-team site and current Birmingham AFA club directory","coordinate_source":"FCHD mapped Coleshill Road ground coordinate"},
]
PROTECTED={norm('Romulus FC'),norm('Sutton Coldfield Town FC')}
text=HTML.read_text(encoding='utf8'); gs,ge=locate(text,'GROUNDS'); grounds=json.loads(text[gs:ge]); es,ee=locate(text,'ELIGIBLE'); eligible=json.loads(text[es:ee])
elig={norm(x.get('name')):x.get('name') for x in eligible if x.get('name')}; existing={norm(g.get('name') or g.get('club')) for g in grounds}
new=[]
for t in TARGETS:
 k=norm(t['name'])
 if k in PROTECTED: raise SystemExit('Safety stop: protected club included.')
 if k not in elig: raise SystemExit(f"Safety stop: {t['name']} not eligible.")
 if k in existing: raise SystemExit(f"Safety stop: existing canonical record for {t['name']}; no overwrite allowed.")
 new.append({"name":elig[k],"ground":t['ground'],"postcode":t['postcode'],"lat":t['lat'],"lon":t['lon'],"verification":"verified","verification_label":"✅ Verified","source":"Current 2026/27 venue evidence: "+t['source'],"ground_source":t['ground_source'],"coordinate_source":t['coordinate_source']})
if len(new)!=2: raise SystemExit('Safety stop: exactly two new records required.')
HTML.write_text(text[:gs]+json.dumps(grounds+sorted(new,key=lambda x:x['name'].lower()),ensure_ascii=False,separators=(',',':'))+text[ge:],encoding='utf8')
now=datetime.now(timezone.utc).isoformat(); payload={"published_at":now,"version":"7.9.11","canonical_records_added":2,"existing_records_overwritten":0,"records":new,"held":{"Hartpury FC":"Temporary five-fixture Gloucester groundshare through 3 October 2026; do not flatten into permanent canonical venue without temporal handling.","Romulus FC":"Protected; no change.","Sutton Coldfield Town FC":"Protected; no change."},"competition_json_changed":False}; OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
lines=['# Tin Foil FA Cup — Critical Ground Batch 6','',f'Published: **{datetime.now(timezone.utc).strftime("%d/%m/%Y, %H:%M:%S UTC")}**','','- New verified canonical records: **2**','- Existing records overwritten: **0**','- Hartpury temporary-venue case published: **NO — held for temporal handling**','- Protected Romulus/Sutton Coldfield records changed: **0**','- `competition.json` changed: **NO**','','## Published records','']
for g in new: lines.append(f"- **{g['name']}** — {g['ground']} • {g['postcode']} • `{g['lat']}, {g['lon']}`")
lines += ['','## Held','','- **Hartpury FC** — own ground remains 4Ed Hartpury Stadium, but five home fixtures from 29 August through 3 October 2026 are temporarily at Gloucester City. This needs time-bounded handling rather than a permanent canonical move.','- **Romulus FC ↔ Sutton Coldfield Town FC** — remains protected pending stronger explicit current relationship evidence.']
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf8')
print('CRITICAL GROUND BATCH 6 v7.9.11'); print('New canonical records: 2'); print('Existing records overwritten: 0'); print('Hartpury: held for temporal handling'); print('Romulus/Sutton Coldfield: untouched')
