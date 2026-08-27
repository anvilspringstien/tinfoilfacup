#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'clubfinder.html'; HEALTH=ROOT/'updater/ground-health.json'; OUT=ROOT/'updater/critical-ground-batch3.json'; REPORT=ROOT/'critical-ground-batch3.md'
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
   if c in ('\'', '"'): ins=True; q=c
   elif c=='[': d+=1
   elif c==']':
    d-=1
    if d==0:return s,i+1
 raise SystemExit('Unbalanced '+name)
TARGETS=[
 {'name':'Darlaston Town FC','ground':'The Paycare Stadium','postcode':'WS2 0EA','lat':52.580972,'lon':-2.022496,'source':'https://www.darlastontown1874fc.com/','ground_source':'Current official club site, 2026/27','coordinate_source':'FCHD mapped Darlaston Town (1874) ground coordinate'},
 {'name':'Everett Rovers FC','ground':'Leggatts Playing Field, Dodd Road','postcode':'WD24 5FS','lat':51.68235,'lon':-0.40511,'source':'https://everettroversfc.co.uk/about-us/','ground_source':'Current official club site plus Watford Council 2026 planning record','coordinate_source':'Geograph subject-location geotag for Everett Rovers pitch (10m precision)'},
 {'name':'Keighley Town FC','ground':'Cougar Park','postcode':'BD21 3RF','lat':53.87545,'lon':-1.90244,'source':'https://keighleycougars.uk/keighley-town-press-release','ground_source':'Current 2026/27 club/owner and NCEL evidence; formerly Eccleshill United','coordinate_source':'OpenStreetMap mapped Cougar Park pitch coordinate'},
 {'name':'Larkfield & New Hythe FC','ground':'Eden Estates Stadium','postcode':'ME20 6PU','lat':51.307222,'lon':0.440844,'source':'https://www.larkfieldandnewhythefc.co.uk/','ground_source':'Current official club and SCEFL 2026/27 directory','coordinate_source':'FCHD 2025-26 mapped Eden Estates Stadium ground coordinate'},
 {'name':'Millbrook FC (Hampshire)','ground':'Test Park Sports Ground','postcode':'SO16 9QZ','lat':50.930429,'lon':-1.467672,'source':'https://www.millbrookfootballclub.com/','ground_source':'Current official club site, 2026/27; Test Park Sports Ground / Solent University','coordinate_source':'FCHD mapped Test Park Sports Ground coordinate; current club postcode supersedes stale FCHD unit'},
 {'name':'Retford FC','ground':'Green Bros. Rail Stadium','postcode':'DN22 7NJ','lat':53.322109,'lon':-0.958108,'source':'https://ncefl.org.uk/teams/retfordfc/','ground_source':'Current 2026/27 NCEL club directory','coordinate_source':'FCHD mapped Babworth Road / Retford ground coordinate'},
 {'name':'Retford United FC','ground':'Cannon Park','postcode':'DN22 0DR','lat':53.324454,'lon':-0.918076,'source':'https://retfordunitedfc.co.uk/contact/','ground_source':'Current official club and 2026/27 NCEL directory','coordinate_source':'FCHD mapped Cannon Park coordinate; current official postcode supersedes older unit'},
 {'name':'Yateley United FC','ground':'Sean Devereux Park','postcode':'GU46 7SZ','lat':51.349647,'lon':-0.830626,'source':'https://www.yateleyunitedfc.co.uk/yufc-community-centre/','ground_source':'Current official club site and 2025 planning documents','coordinate_source':'OS National Grid site reference SU 81534 61823 converted to WGS84'},
 {'name':'Wells City FC','ground':'Athletic Ground','postcode':'BA5 1TU','lat':51.202625,'lon':-2.651614,'source':'https://www.wellscityfc.org.uk/teams/36639','ground_source':'Current official club site, 2026/27','coordinate_source':'FCHD mapped Athletic Ground coordinate'},
 {'name':'Worsbrough Bridge Athletic FC','ground':'Park Road Stadium','postcode':'S70 5LJ','lat':53.526071,'lon':-1.471324,'source':'https://www.ncefl.org.uk/teams/worsbroughbridgeathletic/','ground_source':'Current 2026/27 NCEL club directory','coordinate_source':'FCHD mapped Park Road ground coordinate'}
]
health=json.loads(HEALTH.read_text())
if health.get('counts',{}).get('critical_items')!=25: raise SystemExit('Safety stop: expected 25 critical items before v7.9.8.')
text=HTML.read_text(encoding='utf8'); gs,ge=locate(text,'GROUNDS'); grounds=json.loads(text[gs:ge]); es,ee=locate(text,'ELIGIBLE'); eligible=json.loads(text[es:ee])
ens={norm(x.get('name')):x.get('name') for x in eligible if x.get('name')}; existing={norm(g.get('name') or g.get('club')) for g in grounds}
new=[]
for t in TARGETS:
 k=norm(t['name'])
 if k not in ens: raise SystemExit('Safety stop: not eligible: '+t['name'])
 if k in existing: raise SystemExit('Safety stop: canonical record already exists for '+t['name'])
 new.append({'name':ens[k],'ground':t['ground'],'postcode':t['postcode'],'lat':t['lat'],'lon':t['lon'],'verification':'verified','verification_label':'✅ Verified','source':'Current 2026/27 venue evidence: '+t['source'],'ground_source':t['ground_source'],'coordinate_source':t['coordinate_source']})
if len(new)!=10: raise SystemExit('Safety stop: expected exactly ten records.')
newgrounds=grounds+sorted(new,key=lambda x:x['name'].lower()); HTML.write_text(text[:gs]+json.dumps(newgrounds,ensure_ascii=False,separators=(',',':'))+text[ge:],encoding='utf8')
now=datetime.now(timezone.utc).isoformat(); payload={'published_at':now,'version':'7.9.8','canonical_records_added':10,'existing_records_overwritten':0,'records':new,'excluded_protected':['Romulus FC','Sutton Coldfield Town FC'],'competition_json_changed':False}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
lines=['# Tin Foil FA Cup — Critical Ground Batch 3','',f'Published: **{datetime.now(timezone.utc).strftime("%d/%m/%Y, %H:%M:%S UTC")}**','','**v7.9.8 SAFE PROMOTION**','','- New canonical verified records: **10**','- Existing canonical records overwritten: **0**','- Romulus/Sutton Coldfield changed: **NO**','- `competition.json` changed: **NO**','','## Published records','']
for g in new: lines.append(f"- **{g['name']}** — {g['ground']} • {g['postcode']} • `{g['lat']}, {g['lon']}`")
lines += ['','## Safety','','- Every target was still eligible and missing from canonical `GROUNDS` at runtime.','- No existing canonical record was overwritten.','- Romulus FC and Sutton Coldfield Town FC remain deliberately excluded from this batch.','- `competition.json` is untouched.']
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf8')
print('CRITICAL GROUND BATCH 3 v7.9.8'); print('New canonical records: 10'); print('Overwrites: 0'); print('Romulus/Sutton Coldfield: untouched')
