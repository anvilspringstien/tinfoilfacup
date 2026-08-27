#!/usr/bin/env python3
import json,re
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/'updater/ground-approval-ledger.json'
HTML=ROOT/'clubfinder.html'
REPORT=ROOT/'shared-postcode-review-resolution.md'
OUT=ROOT/'updater/shared-postcode-review-resolution.json'
def norm(s):
 s=(s or '').lower().replace('&',' and ').replace('’',"'"); s=re.sub(r'\b(fc|afc|cfc|football club)\b',' ',s); return re.sub(r'[^a-z0-9]+',' ',s).strip()
def arr(text,name):
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
    if d==0:return json.loads(text[s:i+1])
 raise SystemExit('Unbalanced '+name)
DIRECTED=[
 {"tenant":"AFC Liverpool","host":"Bootle FC","ground":"Berry Street Garage Stadium","postcode":"L30 1NY","season":"2026-27","evidence":"AFC Liverpool announced a groundshare with Bootle from 2025/26 onward and the current NWCFL directory still places AFC Liverpool at Bootle's Berry Street Garage Stadium for 2026/27.","source_url":"https://www.afcliverpool.co.uk/post/afc-liverpool-club-statement"},
 {"tenant":"Baldock Town FC","host":"Arlesey Town FC","ground":"The New Lamb Meadow / Arlesey Town FC","postcode":"SG15 6RS","season":"2026-27","evidence":"Baldock Town's current contact page gives c/o Arlesey Town FC at SG15 6RS, while Arlesey Town's current partnerships page explicitly says it shares its stadium with Baldock Town FC.","source_url":"https://www.arleseytownfc.co.uk/partnerships"},
 {"tenant":"Kennington FC","host":"Ashford United FC","ground":"Homelands Park Stadium","postcode":"TN26 1NJ","season":"2026-27","evidence":"Kennington's current club directory identifies Homelands Stadium (Ashford United FC), and the club's own pre-season material explicitly calls Ashford United its landlords.","source_url":"https://www.kenningtonfc.co.uk/a/scefl-premier-division--directory-56263.html"},
 {"tenant":"Romford FC","host":"Barking FC","ground":"Lawtech Stadium","postcode":"RM8 2JR","season":"2026-27","evidence":"Current 2026/27 Essex Senior League reporting explicitly lists Romford as groundsharing at Barking; Romford's current site gives the Lawtech Stadium, RM8 2JR, as its home address.","source_url":"https://www.harwichandparkeston.com/news/shrimpers-staying-in-esl-2979068.html"},
 {"tenant":"Stone Old Alleynians FC","host":"Newcastle Town FC","ground":"GRG Stadium","postcode":"ST5 3BX","season":"2026-27","evidence":"Stone Old Alleynians' current official site gives GRG Stadium (Newcastle Town FC), ST5 3BX, as its address; current opposition reporting independently describes the ground as shared with Newcastle Town.","source_url":"https://www.pitchero.com/clubs/stoneoldalleyniansfc"},
]
UNDIRECTED=[
 {"clubs":["Gorleston FC","Great Yarmouth Town FC"],"relationship_type":"confirmed_shared_venue_equal_rights_not_groundshare","ground":"The Wellesley Recreation Ground","postcode":"NR30 1EY","season":"2026-27","evidence":"Both clubs are currently playing home fixtures at The Wellesley. Gorleston explicitly states this is NOT a groundshare with Great Yarmouth Town because both clubs have equivalent rights under arrangements with the council-owned facility.","source_url":"https://www.gorlestonfc.com/club-info/Club%20Statement"}
]
HELD=[
 {"postcode":"NE24 3JE","clubs":["Blyth Spartans AFC","Blyth Town FC"],"reason":"Not a current shared venue: Blyth Town's official 2026/27 material and Northern League directory place it at Gateway Park, NE24 3PW. Requires separate canonical venue correction with validated ground coordinates."},
 {"postcode":"NW9 7NE","clubs":["Hendon FC","Hilltop FC"],"reason":"Likely current groundshare, but current first-party direction evidence for Hilltop has not yet met the publication bar. Keep visible pending stronger current evidence."},
 {"postcode":"DN17 2TQ","clubs":["Bottesford Town FC","Bottlesford Town FC"],"reason":"Evidence supports Bottesford Town FC only. 'Bottlesford Town FC' appears to be a duplicate/misspelled club identity rather than a real second ground occupant; do not mutate eligibility/competition data from this ground-review stage."},
 {"postcode":"SW20 9DZ","clubs":["Kingstonian FC","Raynes Park Vale FC"],"reason":"Not a current shared venue: Kingstonian officially ended the Raynes Park Vale agreement after 2025/26 and moved to Ashford Town (Middlesex) for 2026/27. Requires separate canonical venue correction with validated ground coordinates."},
 {"postcode":"B72 1NL","clubs":["Romulus FC","Sutton Coldfield Town FC"],"reason":"Both canonical records are independently verified at Coles Lane, but the relationship remains HELD_FOR_MORE_EVIDENCE by prior safety decision; do not infer direction or approve from postcode alone."}
]
text=HTML.read_text(encoding='utf8'); grounds=arr(text,'GROUNDS'); by={}
for g in grounds: by.setdefault(norm(g.get('name') or g.get('club')),[]).append(g)
for r in DIRECTED:
 tr=by.get(norm(r['tenant']),[]); hr=by.get(norm(r['host']),[])
 if len(tr)!=1 or len(hr)!=1: raise SystemExit('Safety stop canonical resolution: '+r['tenant']+' -> '+r['host'])
 if (tr[0].get('postcode') or '').upper()!=r['postcode'] or (hr[0].get('postcode') or '').upper()!=r['postcode']: raise SystemExit('Safety stop postcode mismatch: '+r['tenant'])
for r in UNDIRECTED:
 for club in r['clubs']:
  rs=by.get(norm(club),[])
  if len(rs)!=1 or (rs[0].get('postcode') or '').upper()!=r['postcode']: raise SystemExit('Safety stop shared venue mismatch: '+club)
ledger=json.loads(LEDGER.read_text(encoding='utf8')); now=datetime.now(timezone.utc).isoformat(); known=ledger.get('known_groundshares') or []
for r in DIRECTED:
 entry={**r,"approved_at":now,"status":"current","approval_source":"v7.9.14 shared-postcode evidence review"}
 known=[x for x in known if norm(x.get('tenant'))!=norm(r['tenant'])]+[entry]
ledger['known_groundshares']=known
shared=ledger.get('known_shared_venues') or []
for r in UNDIRECTED:
 key=tuple(sorted(norm(x) for x in r['clubs']))
 shared=[x for x in shared if tuple(sorted(norm(c) for c in (x.get('clubs') or [])))!=key]+[{**r,"approved_at":now,"status":"current","approval_source":"v7.9.14 shared-postcode evidence review"}]
ledger['known_shared_venues']=shared
ledger['version']='7.9.14'; ledger['updated_at']=now
LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
payload={"resolved_at":now,"version":"7.9.14","directed_groundshares_approved":DIRECTED,"confirmed_shared_venues":UNDIRECTED,"held_or_correction_required":HELD,"canonical_ground_records_changed":0,"competition_json_changed":False}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
lines=['# Tin Foil FA Cup — Shared Postcode Review Resolution','',f'Resolved: **{datetime.now(timezone.utc).strftime("%d/%m/%Y, %H:%M:%S UTC")}**','','- Directed current groundshares approved: **5**','- Confirmed shared venues without forced direction: **1**','- Canonical ground records changed in this stage: **0**','- `competition.json` changed: **NO**','','## Approved directed groundshares','']
for r in DIRECTED: lines.append(f"- **{r['tenant']}** → {r['host']} • {r['postcode']} • {r['season']}")
lines += ['','## Confirmed shared venue without landlord direction','']
for r in UNDIRECTED: lines.append(f"- **{' ↔ '.join(r['clubs'])}** • {r['postcode']} • {r['relationship_type']}")
lines += ['','## Held / separate correction required','']
for r in HELD: lines.append(f"- **{r['postcode']} — {', '.join(r['clubs'])}** — {r['reason']}")
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf8')
print('SHARED POSTCODE REVIEW RESOLUTION v7.9.14')
print('Directed approved: 5')
print('Confirmed shared venue: 1')
print('Held/separate correction required: 5')
print('Canonical records changed: 0')
print('competition.json changed: NO')
