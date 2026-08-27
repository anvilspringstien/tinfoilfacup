#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'clubfinder.html'; OUT=ROOT/'updater/critical-ground-batch4.json'; REPORT=ROOT/'critical-ground-batch4.md'

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
   if c in ("'",'"'): ins=True; q=c
   elif c=='[': d+=1
   elif c==']':
    d-=1
    if d==0:return s,i+1
 raise SystemExit('Unbalanced '+name)

TARGETS=[
 {"name":"AFC Greenwich Borough","ground":"RTL Group Stadium","postcode":"BR2 8HQ","lat":51.37413,"lon":0.03742,"source":"https://greenwichborough.com/","ground_source":"Current official club site, 2026/27","coordinate_source":"FCHD mapped Holmesdale/RTL Group Stadium ground coordinate"},
 {"name":"Dearne & District FC","ground":"Century Cladding Community Welfare Ground","postcode":"S63 9EH","lat":53.528734,"lon":-1.311926,"source":"https://ncefl.org.uk/teams/dearne%26district/","ground_source":"Current NCEL 2026/27 club directory and 2026 home fixture evidence","coordinate_source":"FCHD 2023-24 mapped Welfare Pitch, Furlong Road ground coordinate"},
 {"name":"Desborough Town FC","ground":"Waterworks Field","postcode":"NN14 2LJ","lat":52.445338,"lon":-0.829238,"source":"https://www.artarnfc.co.uk/","ground_source":"Club ground address; independently matched to historic/current Desborough Town identity","coordinate_source":"FCHD 2023-24 mapped Waterworks Ground coordinate"},
 {"name":"Godalming Town FC","ground":"Bill Kyte Stadium","postcode":"GU7 3JE","lat":51.195,"lon":-0.5975,"source":"https://godalmingtownfc.co.uk/find-us/","ground_source":"Current official club directions page","coordinate_source":"Mapped Bill Kyte Stadium ground coordinate cross-checked against current Wey Court address"},
 {"name":"Knowle FC","ground":"The Robins' Nest","postcode":"B93 0NX","lat":52.392759,"lon":-1.733625,"source":"https://www.knowlefc.co.uk/","ground_source":"Current official club site and home fixture listing","coordinate_source":"FCHD mapped Knowle ground coordinate"},
 {"name":"Sturminster Newton United FC","ground":"The We Heat South Stadium, Barnetts Field","postcode":"DT10 1EW","lat":50.935727,"lon":-2.30135,"source":"https://snufc.com/teams/1st-team","ground_source":"Current official 2026/27 first-team page and directions","coordinate_source":"FCHD mapped Barnett's Field ground coordinate"},
 {"name":"Yarm & Eaglescliffe FC","ground":"Bedford Terrace","postcode":"TS23 4AE","lat":54.602338,"lon":-1.282006,"source":"https://yarmeaglescliffefc.uk/","ground_source":"Current official 2026/27 first-team home fixtures and club address at Bedford Terrace","coordinate_source":"Open Postcode Geo point for TS23 4AE; current ground address independently confirmed"},
]
PROTECTED={norm('Romulus FC'),norm('Sutton Coldfield Town FC')}
text=HTML.read_text(encoding='utf8'); gs,ge=locate(text,'GROUNDS'); grounds=json.loads(text[gs:ge]); es,ee=locate(text,'ELIGIBLE'); eligible=json.loads(text[es:ee])
elig={norm(x.get('name')):x.get('name') for x in eligible if x.get('name')}; existing={norm(g.get('name') or g.get('club')) for g in grounds}
new=[]
for t in TARGETS:
 k=norm(t['name'])
 if k in PROTECTED: raise SystemExit('Safety stop: protected relationship club included.')
 if k not in elig: raise SystemExit(f"Safety stop: {t['name']} not eligible.")
 if k in existing: raise SystemExit(f"Safety stop: existing canonical record for {t['name']}; no overwrite allowed.")
 new.append({"name":elig[k],"ground":t['ground'],"postcode":t['postcode'],"lat":t['lat'],"lon":t['lon'],"verification":"verified","verification_label":"✅ Verified","source":"Current 2026/27 venue evidence: "+t['source'],"ground_source":t['ground_source'],"coordinate_source":t['coordinate_source']})
if len(new)!=7: raise SystemExit('Safety stop: exactly seven new records required.')
HTML.write_text(text[:gs]+json.dumps(grounds+sorted(new,key=lambda x:x['name'].lower()),ensure_ascii=False,separators=(',',':'))+text[ge:],encoding='utf8')
now=datetime.now(timezone.utc).isoformat(); payload={"published_at":now,"version":"7.9.9","canonical_records_added":7,"existing_records_overwritten":0,"records":new,"protected_held":["Romulus FC","Sutton Coldfield Town FC"],"competition_json_changed":False}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
lines=['# Tin Foil FA Cup — Critical Ground Batch 4','',f'Published: **{datetime.now(timezone.utc).strftime("%d/%m/%Y, %H:%M:%S UTC")}**','', '- New verified canonical records: **7**','- Existing records overwritten: **0**','- Protected Romulus/Sutton Coldfield records changed: **0**','- `competition.json` changed: **NO**','','## Published records','']
for g in new: lines.append(f"- **{g['name']}** — {g['ground']} • {g['postcode']} • `{g['lat']}, {g['lon']}`")
lines += ['','## Safety','','- Existing canonical `GROUNDS` records are never overwritten.','- Romulus FC and Sutton Coldfield Town FC remain outside this batch.','- Current club/league venue evidence is required; historic fuzzy matches are not accepted on their own.','- `competition.json` is untouched.']
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf8')
print('CRITICAL GROUND BATCH 4 v7.9.9')
print('New canonical records: 7')
print('Existing records overwritten: 0')
print('Romulus/Sutton Coldfield: untouched')
print('competition.json: untouched')
