#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'clubfinder.html'; LEDGER=ROOT/'updater/ground-approval-ledger.json'; OUT=ROOT/'updater/final-shared-postcode-corrections.json'; REPORT=ROOT/'final-shared-postcode-corrections.md'
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
CORRECTIONS=[
 {"name":"Blyth Town FC","old_postcode":"NE24 3JE","ground":"Gateway Park","postcode":"NE24 3PS","lat":55.105842,"lon":-1.519702,"source":"https://blythtownfc.com/contact/","evidence":"Blyth Town's current official club information gives Gateway Park, Sandringham Drive, Blyth, NE24 3PS. Current 2026/27 fixtures are at Gateway Park; mapped ground coordinate is independently supported by FCHD."},
 {"name":"Kingstonian FC","old_postcode":"SW20 9DZ","ground":"Robert Parker Stadium","postcode":"TW19 7BH","lat":51.451958,"lon":-0.462119,"source":"https://www.kingstonianfc.com/generalinfo","evidence":"Kingstonian's current official general information gives Robert Parker Stadium, Short Lane, Stanwell, TW19 7BH as its 2026/27 home. The club announced the move from Raynes Park Vale in March 2026; FCHD supplies the mapped stadium coordinate."}
]
HILLTOP={"tenant":"Hilltop FC","host":"Hendon FC","ground":"Silver Jubilee Park","postcode":"NW9 7NE","season":"2026-27","evidence":"Hilltop FC's own April 2025 club statement confirms a long-term groundshare at Silver Jubilee Park from 2025/26, and current 2026/27 home fixtures remain at Silver Jubilee Park. Hendon's current official site identifies Silver Jubilee Park as its home.","source_url":"https://hilltopfc.co.uk/club-statement-hilltop-fc-confirm-new-ground-share-agreement-from-the-202526-season"}
text=HTML.read_text(encoding='utf8'); gs,ge=locate(text,'GROUNDS'); grounds=json.loads(text[gs:ge]); by={}
for i,g in enumerate(grounds): by.setdefault(norm(g.get('name') or g.get('club')),[]).append((i,g))
changed=[]
for c in CORRECTIONS:
 rs=by.get(norm(c['name']),[])
 if len(rs)!=1: raise SystemExit('Safety stop: expected exactly one canonical record for '+c['name'])
 i,g=rs[0]
 if (g.get('postcode') or '').upper()!=c['old_postcode']: raise SystemExit(f"Safety stop: {c['name']} no longer has expected stale postcode {c['old_postcode']}")
 before={k:g.get(k) for k in ('name','ground','postcode','lat','lon','verification')}
 g.update({"ground":c['ground'],"postcode":c['postcode'],"lat":c['lat'],"lon":c['lon'],"verification":"verified","verification_label":"✅ Verified","source":"Current 2026/27 official venue evidence: "+c['source'],"ground_source":c['evidence'],"coordinate_source":"FCHD mapped football-ground coordinate validated against current official venue"})
 grounds[i]=g; changed.append({"club":c['name'],"before":before,"after":{k:g.get(k) for k in ('name','ground','postcode','lat','lon','verification')},"source":c['source']})
HTML.write_text(text[:gs]+json.dumps(grounds,ensure_ascii=False,separators=(',',':'))+text[ge:],encoding='utf8')
ledger=json.loads(LEDGER.read_text(encoding='utf8')); now=datetime.now(timezone.utc).isoformat(); known=ledger.get('known_groundshares') or []
known=[x for x in known if norm(x.get('tenant'))!=norm(HILLTOP['tenant'])]+[{**HILLTOP,"approved_at":now,"status":"current","approval_source":"v7.9.15 final shared-postcode evidence review"}]
ledger['known_groundshares']=known
vc=ledger.get('venue_corrections') or []
for x in changed:
 vc=[v for v in vc if norm(v.get('club'))!=norm(x['club'])]+[{"club":x['club'],"type":"canonical_current_venue_correction","before":x['before'],"after":x['after'],"source_url":x['source'],"approved_at":now,"approval_source":"v7.9.15 final shared-postcode correction"}]
ledger['venue_corrections']=vc; ledger['version']='7.9.15'; ledger['updated_at']=now; LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
payload={"published_at":now,"version":"7.9.15","canonical_records_corrected":2,"existing_records_added":0,"groundshares_approved":1,"records":changed,"relationship":HILLTOP,"still_held":["Bottesford Town FC / Bottlesford Town FC identity review","Romulus FC / Sutton Coldfield Town FC relationship"],"competition_json_changed":False}; OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
lines=['# Tin Foil FA Cup — Final Shared-Postcode Corrections','',f'Published: **{datetime.now(timezone.utc).strftime("%d/%m/%Y, %H:%M:%S UTC")}**','','- Canonical venue corrections: **2**','- New directed groundshare approvals: **1**','- Existing canonical records overwritten outside named corrections: **0**','- `competition.json` changed: **NO**','','## Canonical corrections','']
for x in changed: lines.append(f"- **{x['club']}** — {x['before']['postcode']} → {x['after']['ground']} • {x['after']['postcode']} • `{x['after']['lat']}, {x['after']['lon']}`")
lines += ['','## Groundshare approved','',f"- **{HILLTOP['tenant']}** → {HILLTOP['host']} • {HILLTOP['postcode']} • {HILLTOP['season']}",'','## Still held','', '- **DN17 2TQ — Bottesford Town FC / Bottlesford Town FC** — club-identity duplication/typo requires eligibility-source resolution, not a groundshare assumption.','- **B72 1NL — Romulus FC / Sutton Coldfield Town FC** — relationship remains `HELD_FOR_MORE_EVIDENCE`; independent canonical records remain valid.']
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf8')
print('FINAL SHARED POSTCODE CORRECTIONS v7.9.15'); print('Canonical corrections: 2'); print('Groundshares approved: 1'); print('competition.json changed: NO')
