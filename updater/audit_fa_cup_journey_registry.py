#!/usr/bin/env python3
from pathlib import Path
import json,re,urllib.request
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'clubfinder.html'
ACCEPTED_URL='https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/accepted-exemptions-and-prize-fund/020726/the-emirates-fa-cup---list-of-clubs-accepted.ashx'; EXEMPTIONS_URL='https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/accepted-exemptions-and-prize-fund/the-emirates-fa-cup---list-of-exemptions.ashx'
ALIASES={'Holmesdale FC':'Petts Wood & Holmesdale FC','Horsham YMCA FC':'Horsham YM FC'}
ROUNDS=('Extra Preliminary Round','Preliminary Round','First Round Qualifying','Second Round Qualifying','Third Round Qualifying','Fourth Round Qualifying','First Round Proper','Second Round Proper','Third Round Proper')
def pdf_pages(url,layout=False):
 from pypdf import PdfReader; import io
 data=urllib.request.urlopen(url,timeout=30).read(); reader=PdfReader(io.BytesIO(data)); out=[]
 for p in reader.pages:
  try:t=p.extract_text(extraction_mode='layout') if layout else p.extract_text()
  except TypeError:t=p.extract_text()
  out.append(t or '')
 return out
def pdf(url):return '\n'.join(pdf_pages(url))
def _base(n):
 s=str(n or '').lower().replace('&',' and '); s=re.sub(r'\b(association football club|football club)\b',' ',s); s=re.sub(r'[^a-z0-9]+',' ',s).strip(); return re.sub(r'\s+',' ',s)
def fa_key(n):
 s=_base(n); s=re.sub(r'\b(fc|cfc)\b',' ',s); s=re.sub(r'\bafc$',' ',s); return re.sub(r'\s+',' ',s).strip()
def ground_key(n):
 s=_base(n); s=re.sub(r'\b(fc|afc|cfc)\b',' ',s); return re.sub(r'\s+',' ',s).strip()
def arr(t,n):
 m=re.search(rf'(?:const|let|var)\s+{re.escape(n)}\s*=\s*(\[.*?\])\s*;',t,re.S)
 if not m:raise SystemExit(f'ABORT: {n} missing')
 return json.loads(m.group(1))
def eround(line):
 u=re.sub(r'\s+',' ',line.upper()).strip()
 for r in ROUNDS:
  if re.fullmatch(rf'\d+\s+CLUBS?\s+EXEMPT TO(?: THE)?\s+{re.escape(r.upper())}(?:\s*\([^)]*\))?',u):return r
 return None
def epr_transition(line):
 u=re.sub(r'\s+',' ',line.upper()).strip()
 return u.startswith('THERE WILL BE 123 STEP 4 CLUBS THAT ARE NOT EXEMPT TO THE PRELIMINARY ROUND AND WILL INSTEAD ENTER THE')
def full_name_present(name,block):
 parts=re.split(r'(\s+)',name); pat=''.join(r'\s+' if p.isspace() else re.escape(p) for p in parts if p)
 return re.search(r'(?<![A-Za-z0-9])'+pat+r'(?![A-Za-z0-9])',block,re.I) is not None
def exemption_variants(name):
 out=[name]
 if re.search(r'\bAFC$',name,re.I):out.append(re.sub(r'\bAFC$','FC',name,flags=re.I))
 if re.search(r'\bFC$',name,re.I):out.append(re.sub(r'\bFC$','AFC',name,flags=re.I))
 return list(dict.fromkeys(out))
h=HTML.read_text(encoding='utf-8'); eligible=arr(h,'ELIGIBLE'); grounds=arr(h,'GROUNDS'); origins=[x.get('name') or x.get('club') for x in eligible if x.get('name') or x.get('club')]; gnames=[x.get('name') or x.get('club') for x in grounds if x.get('name') or x.get('club')]
if len(origins)!=491:raise SystemExit(f'ABORT: expected 491 origins, found {len(origins)}')
ground_keys={ground_key(g) for g in gnames}; origin_ground_missing=[n for n in origins if ground_key(n) not in ground_keys]
if origin_ground_missing:raise SystemExit(f'ABORT: origin without ground under verified-ground identity: {origin_ground_missing}')
lines=[re.sub(r'\s+',' ',x).strip() for x in pdf(ACCEPTED_URL).splitlines()]; clubs=[]
for x in lines:
 if not x or x.startswith('THE EMIRATES FA CUP') or x.startswith('SEASON 2026-27') or 'LIST OF 743 CLUBS' in x or x.startswith('Page ') or len(x)>90 or x.lower().startswith(('the football association','clubs accepted')):continue
 clubs.append(x)
clubs=list(dict.fromkeys(clubs))
if len(clubs)!=743:raise SystemExit(f'ABORT: parsed {len(clubs)} accepted clubs')
accepted_groups=defaultdict(list)
for c in clubs:accepted_groups[fa_key(c)].append(c)
accepted_collisions={k:v for k,v in accepted_groups.items() if len(v)>1}
if accepted_collisions:raise SystemExit(f'ABORT: FA identity collisions require explicit disambiguation: {accepted_collisions}')
accepted={k:v[0] for k,v in accepted_groups.items()}; accepted_exact=set(clubs)
def accepted_names_in_exemption_line(x):
 k=fa_key(x)
 if k in accepted:return [accepted[k]]
 pairs=[]
 for first in clubs:
  for variant in exemption_variants(first):
   if x.startswith(variant):
    rest=x[len(variant):].strip(); rk=fa_key(rest)
    if rk in accepted:pairs.append((first,accepted[rk]))
 pairs=list(dict.fromkeys(pairs))
 if len(pairs)>1:raise SystemExit(f'ABORT: ambiguous concatenated exemption line {x}: {pairs}')
 return list(pairs[0]) if pairs else []
resolved=[]; rec=[]; unmatched=[]
for n in origins:
 if fa_key(n) in accepted:o=accepted[fa_key(n)]
 elif n in ALIASES and fa_key(ALIASES[n]) in accepted:o=accepted[fa_key(ALIASES[n])]; rec.append((n,o))
 else:unmatched.append(n);continue
 resolved.append((n,o))
if unmatched:raise SystemExit(f'ABORT: unmatched origins {unmatched}')
resolved_groups=defaultdict(list)
for n,o in resolved:resolved_groups[fa_key(o)].append(n)
merged={accepted[k]:v for k,v in resolved_groups.items() if len(v)>1}; covered=set(resolved_groups); missing=[c for c in clubs if fa_key(c) not in covered]
if merged:raise SystemExit(f'ABORT: multiple protected origins resolve to one official identity: {merged}')
if len(covered)!=491 or len(missing)!=252 or len(covered)+len(missing)!=743:raise SystemExit(f'ABORT: expected clean 491+252 partition; covered={len(covered)} missing={len(missing)}')
ex_raw=pdf(EXEMPTIONS_URL); ex=[re.sub(r'\s+',' ',x).strip() for x in ex_raw.splitlines() if x.strip()]; rm={}; cur=None; headings=[]; transitions=[]; repaired_lines=[]
for x in ex:
 r=eround(x)
 if r:cur=r;headings.append((x,r));continue
 if epr_transition(x):cur='Extra Preliminary Round';transitions.append(x);continue
 names=accepted_names_in_exemption_line(x)
 if len(names)==2:repaired_lines.append({'raw':x,'clubs':names})
 for name in names:rm[fa_key(name)]=cur
if not headings:raise SystemExit('ABORT: no official exemption headings parsed')
if len(transitions)!=1:raise SystemExit(f'ABORT: expected one Step 4 Extra Preliminary transition, found {len(transitions)}: {transitions}')
layout='\n'.join(pdf_pages(EXEMPTIONS_URL,layout=True)); layout_norm=re.sub(r'[ \t]+',' ',layout)
m32=re.search(r'\(32\)\s*Step\s*5\s*Promoted\s*Clubs',layout_norm,re.I); m91=re.search(r'\(91\)\s*Step\s*4\s*Lowest\s*Ranked\s*\(2025-26\)',layout_norm,re.I)
if not m32 or not m91 or m91.start()<=m32.end():raise SystemExit('ABORT: Step 4 sublist markers not found in layout extraction')
block32=layout_norm[m32.end():m91.start()]; block91=layout_norm[m91.end():]
def names_in_block(block):return [c for c in clubs if any(full_name_present(v,block) for v in exemption_variants(c))]
step5_promoted=names_in_block(block32); step4_lowest=names_in_block(block91)
if len(step5_promoted)!=32:raise SystemExit(f'ABORT: expected 32 Step 5 promoted clubs, parsed {len(step5_promoted)}: {step5_promoted}')
if len(step4_lowest)!=91:raise SystemExit(f'ABORT: expected 91 Step 4 lowest-ranked clubs, parsed {len(step4_lowest)}: {step4_lowest}')
if set(step5_promoted)&set(step4_lowest):raise SystemExit(f'ABORT: club appears in both Step 4 sublists: {sorted(set(step5_promoted)&set(step4_lowest))}')
explicit_epr=step5_promoted+step4_lowest
if len(set(explicit_epr))!=123:raise SystemExit(f'ABORT: Step 4 EPR union is not 123 unique clubs: {len(set(explicit_epr))}')
for c in explicit_epr:rm[fa_key(c)]='Extra Preliminary Round'
counts={}
for c in clubs:
 r=rm.get(fa_key(c),'Extra Preliminary Round');counts[r]=counts.get(r,0)+1
if sum(counts.values())!=743 or any(r not in ROUNDS for r in counts):raise SystemExit(f'ABORT: invalid round counts {counts}')
expected_counts={'Extra Preliminary Round':438,'Preliminary Round':53,'First Round Qualifying':88,'Second Round Qualifying':48,'Fourth Round Qualifying':24,'First Round Proper':48,'Third Round Proper':44}
for r,n in expected_counts.items():
 if counts.get(r)!=n:raise SystemExit(f'ABORT: expected {n} entrants for {r}, got {counts.get(r)}; counts={counts}')
gby=defaultdict(list)
for n in gnames:gby[ground_key(n)].append(n)
queue=[]
for c in missing:
 candidates=gby.get(ground_key(c),[])
 if len(candidates)>1:raise SystemExit(f'ABORT: ambiguous existing GROUNDS match for {c}: {candidates}')
 e=candidates[0] if candidates else None
 queue.append({'club':c,'entry_round':rm.get(fa_key(c),'Extra Preliminary Round'),'existing_ground_record':e,'verification_status':'existing-ground-record-needs-registry-review' if e else 'pending'})
existing=sum(bool(x['existing_ground_record']) for x in queue); pending=len(queue)-existing
report={'official_accepted':743,'protected_origin_records':491,'protected_origin_ground_matches':491,'reconciled_official_origin_identities':len(covered),'identity_reconciliations':[{'origin_name':a,'official_name':b} for a,b in rec],'additional_journey_clubs':len(missing),'raw_ground_records':len(gnames),'additional_clubs_with_existing_ground_record':existing,'additional_clubs_pending_ground_verification':pending,'entry_round_counts':counts,'step5_promoted_epr_clubs':len(step5_promoted),'step4_lowest_ranked_epr_clubs':len(step4_lowest),'additional_clubs':queue,'read_only':True}
(ROOT/'updater'/'fa-cup-journey-registry-audit.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'updater'/'journey-club-verification-queue.json').write_text(json.dumps({'clubs':queue},indent=2)+'\n')
md=['# FA Cup Journey Registry — Read-only reconciliation','','- Official accepted clubs: **743**','- Protected origin records: **491**','- Protected origin→GROUNDS matches: **491**',f'- Reconciled official origin identities: **{len(covered)}**',f'- Additional journey clubs: **{len(missing)}**',f'- Existing ground records among additional clubs: **{existing}**',f'- Pending ground verification: **{pending}**','- Step 5 promoted clubs entering Extra Preliminary: **32**','- Step 4 lowest-ranked clubs entering Extra Preliminary: **91**','','## Identity reconciliations']+[f'- {a} → {b}' for a,b in rec]+['','## Entry-round population']+[f'- {r}: **{counts[r]}**' for r in ROUNDS if r in counts]+['','## Verification queue']+[f"- {x['club']} — {x['entry_round']}"+(f" — existing GROUNDS: {x['existing_ground_record']}" if x['existing_ground_record'] else '') for x in queue]+['','## Safety','- READ ONLY. Canonical Clubfinder, competition, grounds, mileage and journey data untouched.','- Separate FA identity and verified-ground identity namespaces.','- Leading AFC is identity-significant; trailing AFC/FC suffix variants reconcile only through a unique official identity.','- Exact 491 + 252 = 743 partition required.','- Entry-round totals cross-checked against official headings and the 219-tie Extra Preliminary draw.','- The Step 4 exception is independently validated as 32 promoted Step 5 + 91 lowest-ranked Step 4 = 123 clubs using layout-mode PDF extraction and full-name boundaries.']
(ROOT/'fa-cup-journey-registry-audit.md').write_text('\n'.join(md)+'\n')
print('FA CUP JOURNEY REGISTRY AUDIT: SUCCESS');print('Protected origin-ground matches: 491');print('Covered official identities:',len(covered));print('Additional:',len(missing));print('Existing ground records:',existing);print('Pending:',pending);print('Entry rounds:',counts);print('Step 5 promoted EPR:',len(step5_promoted));print('Step 4 lowest-ranked EPR:',len(step4_lowest));print('READ ONLY')