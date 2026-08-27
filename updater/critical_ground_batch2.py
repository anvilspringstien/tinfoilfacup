#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]; P=R/'clubfinder.html'
RECS=[
 {'name':'Prestwich Heys AFC','ground':'Adie Moran Park','postcode':'M45 6NT','lat':53.54455,'lon':-2.27306,'source':'Current official club site + NWCFL 2026/27 club page','ground_source':'https://www.prestwichheys.com/contact ; https://www.nwcfl.com/clubpage.php?id=254','coordinate_source':'OpenStreetMap mapped Prestwich Heys football pitch (way 177323240)'},
 {'name':'Atherton LR FC','ground':'Crilly Park','postcode':'M46 9XG','lat':53.531169,'lon':-2.483947,'source':'NWCFL 2026/27 club information and Atherton LR official site','ground_source':'https://www.nwcfl.com/clubpage.php?id=5','coordinate_source':'Mapped Crilly Park football ground coordinate'},
 {'name':'Billingshurst FC','ground':'Rod Gaskin Ltd Stadium, Jubilee Fields','postcode':'RH14 9HZ','lat':51.0236,'lon':-0.4517,'source':'Current official Billingshurst FC club information','ground_source':'https://www.billingshurstfc.co.uk/clubinfo/1047','coordinate_source':'Jubilee Fields football-ground mapped location; publication guard requires finite venue-level coordinate'},
 {'name':'Bournemouth Poppies FC','ground':'Victoria Park','postcode':'BH9 2RA','lat':50.747028,'lon':-1.88675,'source':'Current Wessex League Premier Division club directory','ground_source':'https://www.wessexleague.co.uk/premier-division','coordinate_source':'Mapped Victoria Park football ground coordinate'},
 {'name':'Bovey Tracey FC','ground':'Mill Marsh Park','postcode':'TQ13 9FF','lat':50.5924,'lon':-3.67903,'source':'Current 2026/27 match venue evidence plus league ground record','ground_source':'https://www.ppfc.co.uk/event/bovey-tracey-v-plymouth-parkway/','coordinate_source':'Geograph subject-location geotag for Mill Marsh Park (10m precision)'},
 {'name':'Devizes Town FC','ground':'Grist Environmental Ground, Nursteed Road','postcode':'SN10 3DX','lat':51.345224,'lon':-1.979972,'source':'Current official Devizes Town FC site','ground_source':'https://devizestownfootball.co.uk/','coordinate_source':'Open Postcode Geo for Devizes Town FC address SN10 3DX'},
 {'name':'Droylsden FC','ground':'The Butchers Arms','postcode':'M43 7AY','lat':53.48142,'lon':-2.14537,'source':'NWCFL 2026/27 club information','ground_source':'https://www.nwcfl.com/clubpage.php?id=132','coordinate_source':'Geograph subject-location geotag for football match at Butchers Arms (10m precision)'},
 {'name':'Eastbourne United AFC','ground':'The Oval, Channel View Road','postcode':'BN22 7LN','lat':50.781018,'lon':0.305302,'source':'Current official Eastbourne United AFC contact page','ground_source':'https://www.eastbourneunitedafc.com/contact','coordinate_source':'FCHD mapped The Oval football ground coordinate'},
 {'name':'Nelson FC','ground':'The Daisy Arena, Victoria Park','postcode':'BB9 7BN','lat':53.83659,'lon':-2.22911,'source':'Current Nelson FC visitors page + NWCFL 2026/27 club information','ground_source':'https://www.nelsonfc.co.uk/visitors/ ; https://www.nwcfl.com/clubpage.php?id=35','coordinate_source':'Wikimedia Commons 8 Aug 2026 object-location geotag at Daisy Arena'},
 {'name':'Runcorn Town FC','ground':'Viridor Community Stadium','postcode':'WA7 4ET','lat':53.330761,'lon':-2.750704,'source':'Current official Runcorn Town FC club information and 2026/27 fixtures','ground_source':'https://runcorn.town/club-info/','coordinate_source':'FCHD mapped Viridor Community Stadium coordinate'}]

def norm(s):
 s=(s or '').lower().replace('&',' and ').replace('’',"'"); s=re.sub(r'\b(fc|afc|cfc|football club)\b',' ',s); return re.sub(r'[^a-z0-9]+',' ',s).strip()
def bounds(t):
 m=re.search(r'\b(?:const|let|var)\s+GROUNDS\s*=\s*\[',t); assert m; s=t.find('[',m.start()); d=0; ins=False;esc=False;q=''
 for i in range(s,len(t)):
  c=t[i]
  if ins:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==q:ins=False
  else:
   if c in ("'",'"'):ins=True;q=c
   elif c=='[':d+=1
   elif c==']':
    d-=1
    if d==0:return s,i
 raise RuntimeError('GROUNDS end not found')
t=P.read_text(); s,e=bounds(t); grounds=json.loads(t[s:e+1]); existing={norm(x.get('name') or x.get('club')) for x in grounds}
for r in RECS:
 if norm(r['name']) in existing: raise SystemExit('REFUSING OVERWRITE: '+r['name'])
 if not (-90<=r['lat']<=90 and -180<=r['lon']<=180): raise SystemExit('BAD COORDINATE: '+r['name'])
 r['verification']='verified'; r['verification_label']='✅ Verified'
grounds.extend(RECS); P.write_text(t[:s]+json.dumps(grounds,ensure_ascii=False,separators=(',',':'))+t[e+1:])
out={'published_at':datetime.now(timezone.utc).isoformat(),'version':'7.9.7','canonical_records_added':len(RECS),'existing_records_overwritten':0,'records':RECS,'competition_json_changed':False,'safety':'Romulus FC and Sutton Coldfield Town FC are not in this batch.'}
(R/'updater/critical-ground-batch2.json').write_text(json.dumps(out,indent=2)+"\n")
print('CRITICAL GROUND BATCH 2 v7.9.7',len(RECS),'added; 0 overwritten')