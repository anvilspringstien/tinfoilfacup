#!/usr/bin/env python3
from pathlib import Path
import json,re,urllib.request
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'clubfinder.html'
ACCEPTED_URL='https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/accepted-exemptions-and-prize-fund/020726/the-emirates-fa-cup---list-of-clubs-accepted.ashx'; EXEMPTIONS_URL='https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/accepted-exemptions-and-prize-fund/the-emirates-fa-cup---list-of-exemptions.ashx'
ALIASES={'Holmesdale FC':'Petts Wood & Holmesdale FC','Horsham YMCA FC':'Horsham YM FC'}
ROUNDS=('Extra Preliminary Round','Preliminary Round','First Round Qualifying','Second Round Qualifying','Third Round Qualifying','Fourth Round Qualifying','First Round Proper','Second Round Proper','Third Round Proper')
def pdf(url):
 from pypdf import PdfReader; import io
 return '\n'.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(urllib.request.urlopen(url,timeout=30).read())).pages)
def key(n):
 s=str(n or '').lower().replace('&',' and '); s=re.sub(r'\b(association football club|football club)\b',' ',s); s=re.sub(r'\b(fc|cfc)\b',' ',s); s=re.sub(r'[^a-z0-9]+',' ',s).strip(); return re.sub(r'\s+',' ',s)
def arr(t,n):
 m=re.search(rf'(?:const|let|var)\s+{re.escape(n)}\s*=\s*(\[.*?\])\s*;',t,re.S)
 if not m:raise SystemExit(f'ABORT: {n} missing')
 return json.loads(m.group(1))
def eround(line):
 u=re.sub(r'\s+',' ',line.upper()).strip()
 return next((r for r in ROUNDS if 'EXEMPT TO' in u and r.upper() in u),None)
h=HTML.read_text(encoding='utf-8'); eligible=arr(h,'ELIGIBLE'); grounds=arr(h,'GROUNDS'); origins=[x.get('name') or x.get('club') for x in eligible if x.get('name') or x.get('club')]; gnames=[x.get('name') or x.get('club') for x in grounds if x.get('name') or x.get('club')]
if len(origins)!=491:raise SystemExit(f'ABORT: expected 491 origins, found {len(origins)}')
if [n for n in origins if key(n) not in {key(g) for g in gnames}]:raise SystemExit('ABORT: origin without ground')
lines=[re.sub(r'\s+',' ',x).strip() for x in pdf(ACCEPTED_URL).splitlines()]; clubs=[]
for x in lines:
 if not x or x.startswith('THE EMIRATES FA CUP') or x.startswith('SEASON 2026-27') or 'LIST OF 743 CLUBS' in x or x.startswith('Page ') or len(x)>90 or x.lower().startswith(('the football association','clubs accepted')):continue
 clubs.append(x)
clubs=list(dict.fromkeys(clubs))
if len(clubs)!=743:raise SystemExit(f'ABORT: parsed {len(clubs)} accepted clubs')
accepted_groups=defaultdict(list)
for c in clubs:accepted_groups[key(c)].append(c)
accepted_collisions={k:v for k,v in accepted_groups.items() if len(v)>1}
if accepted_collisions:raise SystemExit(f'ABORT: canonical-key collisions in official accepted list require explicit disambiguation: {accepted_collisions}')
accepted={k:v[0] for k,v in accepted_groups.items()}; resolved=[]; rec=[]; unmatched=[]
for n in origins:
 if key(n) in accepted:o=accepted[key(n)]
 elif n in ALIASES and key(ALIASES[n]) in accepted:o=accepted[key(ALIASES[n])]; rec.append((n,o))
 else:unmatched.append(n);continue
 resolved.append((n,o))
if unmatched:raise SystemExit(f'ABORT: unmatched origins {unmatched}')
resolved_groups=defaultdict(list)
for n,o in resolved:resolved_groups[key(o)].append(n)
merged={accepted[k]:v for k,v in resolved_groups.items() if len(v)>1}; covered=set(resolved_groups); missing=[c for c in clubs if key(c) not in covered]
if len(covered)+len(missing)!=743:raise SystemExit(f'ABORT: partition mismatch covered={len(covered)} missing={len(missing)} merged={merged}')
ex=[re.sub(r'\s+',' ',x).strip() for x in pdf(EXEMPTIONS_URL).splitlines() if x.strip()]; rm={}; cur=None
for x in ex:
 r=eround(x)
 if r:cur=r;continue
 if cur and key(x) in accepted:rm[key(x)]=cur
counts={}
for c in clubs:
 r=rm.get(key(c),'Extra Preliminary Round');counts[r]=counts.get(r,0)+1
if sum(counts.values())!=743 or any(r not in ROUNDS for r in counts):raise SystemExit(f'ABORT: invalid round counts {counts}')
gby={key(n):n for n in gnames}; queue=[]
for c in missing:
 e=gby.get(key(c));queue.append({'club':c,'entry_round':rm.get(key(c),'Extra Preliminary Round'),'existing_ground_record':e,'verification_status':'existing-ground-record-needs-registry-review' if e else 'pending'})
existing=sum(bool(x['existing_ground_record']) for x in queue); pending=len(queue)-existing
report={'official_accepted':743,'protected_origin_records':491,'reconciled_official_origin_identities':len(covered),'identity_reconciliations':[{'origin_name':a,'official_name':b} for a,b in rec],'merged_origin_identities':[{'official_name':o,'origin_records':v} for o,v in merged.items()],'additional_journey_clubs':len(missing),'raw_ground_records':len(gnames),'additional_clubs_with_existing_ground_record':existing,'additional_clubs_pending_ground_verification':pending,'entry_round_counts':counts,'additional_clubs':queue,'read_only':True}
(ROOT/'updater'/'fa-cup-journey-registry-audit.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'updater'/'journey-club-verification-queue.json').write_text(json.dumps({'clubs':queue},indent=2)+'\n')
md=['# FA Cup Journey Registry — Read-only reconciliation','',f'- Official accepted clubs: **743**',f'- Protected origin records: **491**',f'- Reconciled official origin identities: **{len(covered)}**',f'- Additional journey clubs: **{len(missing)}**',f'- Existing ground records among additional clubs: **{existing}**',f'- Pending ground verification: **{pending}**','','## Identity reconciliations']+[f'- {a} → {b}' for a,b in rec]+['','## Merged origin identities']+([f"- {o} ← {', '.join(v)}" for o,v in merged.items()] or ['- None'])+['','## Entry-round population']+[f'- {r}: **{counts[r]}**' for r in ROUNDS if r in counts]+['','## Verification queue']+[f"- {x['club']} — {x['entry_round']}"+(f" — existing GROUNDS: {x['existing_ground_record']}" if x['existing_ground_record'] else '') for x in queue]+['','## Safety','- READ ONLY. Canonical Clubfinder, competition, grounds, mileage and journey data untouched.','- AFC is identity-significant; explicit aliases only; ambiguous canonical collisions fail closed.']
(ROOT/'fa-cup-journey-registry-audit.md').write_text('\n'.join(md)+'\n')
print('FA CUP JOURNEY REGISTRY AUDIT: SUCCESS');print('Covered official identities:',len(covered));print('Merged:',merged);print('Additional:',len(missing));print('Existing ground records:',existing);print('Pending:',pending);print('Entry rounds:',counts);print('READ ONLY')