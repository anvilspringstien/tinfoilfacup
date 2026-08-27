#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'clubfinder.html'; LEDGER=ROOT/'updater/ground-approval-ledger.json'; OUT=ROOT/'updater/final-protected-ground-records.json'; REPORT=ROOT/'final-protected-ground-records.md'
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
 {"name":"Romulus FC","ground":"The Central Ground","postcode":"B72 1NL","lat":52.556733,"lon":-1.818659,"source":"https://runcorn.town/2026-27-fixtures-released/","ground_source":"Independent current 2026/27 MFL opponent fixture schedule plus 2026/27 FA Cup venue evidence place Romulus home fixtures at Central Ground, Coles Lane","coordinate_source":"FCHD mapped Central Ground/Coles Lane coordinate"},
 {"name":"Sutton Coldfield Town FC","ground":"The Domino's Arena","postcode":"B72 1NL","lat":52.556733,"lon":-1.818659,"source":"https://www.sctfc.com/ground","ground_source":"Current official Sutton Coldfield Town ground page and 2026/27 first-team site","coordinate_source":"FCHD mapped Central Ground/Coles Lane coordinate"},
]
text=HTML.read_text(encoding='utf8'); gs,ge=locate(text,'GROUNDS'); grounds=json.loads(text[gs:ge]); es,ee=locate(text,'ELIGIBLE'); eligible=json.loads(text[es:ee])
elig={norm(x.get('name')):x.get('name') for x in eligible if x.get('name')}; existing={norm(g.get('name') or g.get('club')) for g in grounds}
new=[]
for t in TARGETS:
 k=norm(t['name'])
 if k not in elig: raise SystemExit(f"Safety stop: {t['name']} not eligible.")
 if k in existing: raise SystemExit(f"Safety stop: existing canonical record for {t['name']}; no overwrite allowed.")
 new.append({"name":elig[k],"ground":t['ground'],"postcode":t['postcode'],"lat":t['lat'],"lon":t['lon'],"verification":"verified","verification_label":"✅ Verified","source":"Independent current 2026/27 venue evidence: "+t['source'],"ground_source":t['ground_source'],"coordinate_source":t['coordinate_source']})
if len(new)!=2: raise SystemExit('Safety stop: exactly two independent records required.')
HTML.write_text(text[:gs]+json.dumps(grounds+sorted(new,key=lambda x:x['name'].lower()),ensure_ascii=False,separators=(',',':'))+text[ge:],encoding='utf8')
# Explicitly preserve the unresolved relationship as HELD. It is deliberately NOT added to known_groundshares.
ledger=json.loads(LEDGER.read_text(encoding='utf8')); now=datetime.now(timezone.utc).isoformat(); known=ledger.get('known_groundshares') or []
if any(norm(x.get('tenant')) in {norm('Romulus FC'),norm('Sutton Coldfield Town FC')} for x in known): raise SystemExit('Safety stop: protected relationship already appears in known_groundshares.')
held=ledger.get('held_groundshare_relationships') or []
entry={"clubs":["Romulus FC","Sutton Coldfield Town FC"],"postcode":"B72 1NL","status":"HELD_FOR_MORE_EVIDENCE","reason":"Each club now has an independently evidenced current canonical ground record at Coles Lane. Shared current venue does not by itself establish tenant/host direction or a groundshare relationship, so no relationship is approved.","recorded_at":now,"source":"v7.9.13 independent canonical verification"}
held=[x for x in held if set(x.get('clubs') or [])!=set(entry['clubs'])]+[entry]; ledger['held_groundshare_relationships']=held; ledger['version']='7.9.13'; ledger['updated_at']=now; LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
payload={"published_at":now,"version":"7.9.13","canonical_records_added":2,"existing_records_overwritten":0,"groundshare_relationships_approved":0,"held_relationships_recorded":1,"records":new,"held":entry,"competition_json_changed":False}; OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
lines=['# Tin Foil FA Cup — Final Protected Ground Records','',f'Published: **{datetime.now(timezone.utc).strftime("%d/%m/%Y, %H:%M:%S UTC")}**','','- Independent verified canonical records added: **2**','- Existing canonical records overwritten: **0**','- Groundshare relationships approved: **0**','- Held relationship records retained/recorded: **1**','- `competition.json` changed: **NO**','','## Independent canonical records','']
for g in new: lines.append(f"- **{g['name']}** — {g['ground']} • {g['postcode']} • `{g['lat']}, {g['lon']}`")
lines += ['','## Relationship status','','- **Romulus FC ↔ Sutton Coldfield Town FC** remains `HELD_FOR_MORE_EVIDENCE`.','- The fact that both independently resolve to Coles Lane/B72 1NL is not treated as proof of tenant/host direction.','- Ground Health should therefore continue to show the shared postcode as a review item rather than suppressing it as approved.','','## Safety','','- No existing canonical record was overwritten.','- Neither club was inferred from the other; each has independent current evidence.','- No entry was added to `known_groundshares`.','- `competition.json` is untouched.']
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf8')
print('FINAL PROTECTED GROUND RECORDS v7.9.13'); print('Canonical records added: 2'); print('Groundshares approved: 0'); print('Relationship: HELD_FOR_MORE_EVIDENCE'); print('competition.json: untouched')
