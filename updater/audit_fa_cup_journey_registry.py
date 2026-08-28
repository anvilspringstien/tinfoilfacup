#!/usr/bin/env python3
"""Read-only reconciliation of the official 2026-27 FA Cup field against Clubfinder's verified origin clubs."""
from pathlib import Path
import json, re, urllib.request
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'clubfinder.html'
OUT_MD=ROOT/'fa-cup-journey-registry-audit.md'; OUT_JSON=ROOT/'updater'/'fa-cup-journey-registry-audit.json'; OUT_QUEUE=ROOT/'updater'/'journey-club-verification-queue.json'
ACCEPTED_URL='https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/accepted-exemptions-and-prize-fund/020726/the-emirates-fa-cup---list-of-clubs-accepted.ashx'
EXEMPTIONS_URL='https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/accepted-exemptions-and-prize-fund/the-emirates-fa-cup---list-of-exemptions.ashx'
IDENTITY_ALIASES={'Holmesdale FC':'Petts Wood & Holmesdale FC','Horsham YMCA FC':'Horsham YM FC'}
ROUND_NAMES=('Extra Preliminary Round','Preliminary Round','First Round Qualifying','Second Round Qualifying','Third Round Qualifying','Fourth Round Qualifying','First Round Proper','Second Round Proper','Third Round Proper')
def pdf_text(url):
 data=urllib.request.urlopen(url,timeout=30).read(); from pypdf import PdfReader; import io
 return '\n'.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(data)).pages)
def key(name):
 s=str(name or '').lower().replace('&',' and '); s=re.sub(r'\b(association football club|football club)\b',' ',s); s=re.sub(r'\b(fc|afc|cfc)\b',' ',s); s=re.sub(r'[^a-z0-9]+',' ',s).strip(); return re.sub(r'\s+',' ',s)
def extract_js_array(text,name):
 m=re.search(rf'(?:const|let|var)\s+{re.escape(name)}\s*=\s*(\[.*?\])\s*;',text,re.S)
 if not m: raise SystemExit(f'ABORT: {name} array not found')
 return json.loads(m.group(1))
def exemption_round(line):
 u=re.sub(r'\s+',' ',line.upper()).strip()
 if 'EXEMPT TO' not in u:return None
 return next((r for r in ROUND_NAMES if r.upper() in u),None)
html=HTML.read_text(encoding='utf-8'); eligible=extract_js_array(html,'ELIGIBLE'); grounds=extract_js_array(html,'GROUNDS')
origin_names=[x.get('name') or x.get('club') for x in eligible if x.get('name') or x.get('club')]
if len(origin_names)!=491:raise SystemExit(f'ABORT: expected 491 ELIGIBLE origin clubs, found {len(origin_names)}')
ground_names=[x.get('name') or x.get('club') for x in grounds if x.get('name') or x.get('club')]; ground_keys={key(n) for n in ground_names}
no_ground=[n for n in origin_names if key(n) not in ground_keys]
if no_ground:raise SystemExit(f'ABORT: protected origins without GROUNDS: {no_ground}')
origin_keys={key(n) for n in origin_names}; later_ground=[n for n in ground_names if key(n) not in origin_keys]
lines=[re.sub(r'\s+',' ',x).strip() for x in pdf_text(ACCEPTED_URL).splitlines()]; clubs=[]
for line in lines:
 if not line or line.startswith('THE EMIRATES FA CUP') or line.startswith('SEASON 2026-27') or 'LIST OF 743 CLUBS' in line or line.startswith('Page '):continue
 if len(line)>90 or line.lower().startswith(('the football association','clubs accepted')):continue
 clubs.append(line)
clubs=list(dict.fromkeys(clubs))
if len(clubs)!=743:raise SystemExit(f'ABORT: official accepted parser expected 743, parsed {len(clubs)}')
accepted_by_key={key(n):n for n in clubs}; resolved=[]; reconciliations=[]; unmatched=[]
for n in origin_names:
 if key(n) in accepted_by_key: official=accepted_by_key[key(n)]
 elif n in IDENTITY_ALIASES and key(IDENTITY_ALIASES[n]) in accepted_by_key:
  official=accepted_by_key[key(IDENTITY_ALIASES[n])]; reconciliations.append({'origin_name':n,'official_name':official})
 else: unmatched.append(n); continue
 resolved.append((n,official))
if unmatched:raise SystemExit(f'ABORT: protected origin identities unmatched: {unmatched}')
by_official=defaultdict(list)
for origin,official in resolved:by_official[key(official)].append(origin)
merged=[{'official_name':accepted_by_key[k],'origin_records':v} for k,v in by_official.items() if len(v)>1]
resolved_keys=set(by_official); missing=[c for c in clubs if key(c) not in resolved_keys]
# Do not assume arithmetic after mergers/renames: the official unique-identity set is authoritative.
if len(resolved_keys)+len(missing)!=743:raise SystemExit('ABORT: reconciled identity partition does not total 743')
ex_lines=[re.sub(r'\s+',' ',x).strip() for x in pdf_text(EXEMPTIONS_URL).splitlines() if x.strip()]; round_map={}; current=None
for line in ex_lines:
 r=exemption_round(line)
 if r:current=r;continue
 if current and key(line) in accepted_by_key:round_map[key(line)]=current
entry_counts={}
for c in clubs:
 r=round_map.get(key(c),'Extra Preliminary Round'); entry_counts[r]=entry_counts.get(r,0)+1
if sum(entry_counts.values())!=743 or any(r not in ROUND_NAMES for r in entry_counts):raise SystemExit(f'ABORT: invalid entry-round population: {entry_counts}')
ground_by_key={key(n):n for n in ground_names}; queue=[]
for c in missing:
 existing=ground_by_key.get(key(c)); queue.append({'club':c,'entry_round':round_map.get(key(c),'Extra Preliminary Round'),'existing_ground_record':existing,'verification_status':'existing-ground-record-needs-registry-review' if existing else 'pending'})
existing_count=sum(bool(x['existing_ground_record']) for x in queue); pending=len(queue)-existing_count
report={'official_accepted':743,'protected_origin_records':491,'reconciled_official_origin_identities':len(resolved_keys),'identity_reconciliations':reconciliations,'merged_origin_identities':merged,'additional_journey_clubs':len(missing),'raw_ground_records':len(ground_names),'later_round_ground_records_outside_origin_population':len(later_ground),'additional_clubs_with_existing_ground_record':existing_count,'additional_clubs_pending_ground_verification':pending,'entry_round_counts':entry_counts,'additional_clubs':queue,'later_round_ground_records':later_ground,'sources':{'accepted':ACCEPTED_URL,'exemptions':EXEMPTIONS_URL},'read_only':True}
OUT_JSON.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); OUT_QUEUE.write_text(json.dumps({'generated_by':'audit_fa_cup_journey_registry.py','read_only_source_audit':True,'clubs':queue},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
md=['# FA Cup Journey Registry — Read-only reconciliation','',f'- Official accepted clubs: **743**',f'- Protected origin records: **491**',f'- Reconciled official origin identities: **{len(resolved_keys)}**',f'- Additional journey clubs: **{len(missing)}**',f'- Existing ground records among additional clubs: **{existing_count}**',f'- Pending ground verification: **{pending}**','','## Explicit identity reconciliations']
for x in reconciliations:md.append(f"- {x['origin_name']} → {x['official_name']}")
md+=['','## Merged/duplicate official identities represented by multiple origin records']
md += [f"- {x['official_name']} ← {', '.join(x['origin_records'])}" for x in merged] or ['- None']
md+=['','## Official entry-round population']
for r in ROUND_NAMES:
 if r in entry_counts:md.append(f'- {r}: **{entry_counts[r]}**')
md+=['','## Additional journey-club verification queue']
for x in queue:md.append(f"- {x['club']} — {x['entry_round']}"+(f" — existing GROUNDS record: {x['existing_ground_record']}" if x['existing_ground_record'] else ''))
md+=['','## Safety','- READ ONLY: no Clubfinder, competition, ground, venue, mileage or journey data was changed.','- ELIGIBLE remains the protected 491 origin-record population.','- Official unique club identities, not raw historic record arithmetic, define the additional journey-club count.','- Identity reconciliation uses explicit evidence-backed aliases only; no fuzzy identity guesses.']
OUT_MD.write_text('\n'.join(md)+'\n',encoding='utf-8')
print('FA CUP JOURNEY REGISTRY AUDIT: SUCCESS'); print('Official accepted: 743'); print('Protected origin records: 491'); print('Reconciled official origin identities:',len(resolved_keys)); print('Merged origin identities:',merged); print('Additional journey clubs:',len(missing)); print('Existing ground records in queue:',existing_count); print('Pending ground verification:',pending); print('Entry rounds:',entry_counts); print('READ ONLY: canonical data untouched')
