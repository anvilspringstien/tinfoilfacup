#!/usr/bin/env python3
"""Read-only official FA reconciliation for Law 2 origins and companion registry."""
from pathlib import Path
import json,re,urllib.request
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]; HTML=ROOT/'clubfinder.html'
ACCEPTED_URL='https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/accepted-exemptions-and-prize-fund/020726/the-emirates-fa-cup---list-of-clubs-accepted.ashx'; EXEMPTIONS_URL='https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/accepted-exemptions-and-prize-fund/the-emirates-fa-cup---list-of-exemptions.ashx'
ALIASES={'Holmesdale FC':'Petts Wood & Holmesdale FC','Horsham YMCA FC':'Horsham YM FC'}
EXEMPTION_DOCUMENT_ALIASES={'Bedfont Sports Club FC':['Bedfont Sports FC']}
ROUNDS=('Extra Preliminary Round','Preliminary Round','First Round Qualifying','Second Round Qualifying','Third Round Qualifying','Fourth Round Qualifying','First Round Proper','Second Round Proper','Third Round Proper')
LAW2_ROUNDS={'Extra Preliminary Round','Preliminary Round','First Round Qualifying','Second Round Qualifying','Fourth Round Qualifying'}
BASELINE_ROUNDS={'Extra Preliminary Round','Preliminary Round'}
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
def arr(t,n,required=True):
 m=re.search(rf'(?:const|let|var)\s+{re.escape(n)}\s*=\s*(\[.*?\])\s*;',t,re.S)
 if not m:
  if required:raise SystemExit(f'ABORT: {n} missing')
  return []
 return json.loads(m.group(1))
def eround(line):
 u=re.sub(r'\s+',' ',line.upper()).strip()
 for r in ROUNDS:
  if re.fullmatch(rf'\d+\s+CLUBS?\s+EXEMPT TO(?: THE)?\s+{re.escape(r.upper())}(?:\s*\([^)]*\))?',u):return r
 return None
def epr_transition(line):
 u=re.sub(r'\s+',' ',line.upper()).strip(); return u.startswith('THERE WILL BE 123 STEP 4 CLUBS THAT ARE NOT EXEMPT TO THE PRELIMINARY ROUND AND WILL INSTEAD ENTER THE')
def full_name_present(name,block):
 parts=re.split(r'(\s+)',name); pat=''.join(r'\s+' if p.isspace() else re.escape(p) for p in parts if p); return re.search(r'(?<![A-Za-z0-9])'+pat+r'(?![A-Za-z0-9])',block,re.I) is not None
def exemption_variants(name):
 out=[name]
 if re.search(r'\bAFC$',name,re.I):out.append(re.sub(r'\bAFC$','FC',name,flags=re.I))
 if re.search(r'\bFC$',name,re.I):out.append(re.sub(r'\bFC$','AFC',name,flags=re.I))
 out.extend(EXEMPTION_DOCUMENT_ALIASES.get(name,[])); return list(dict.fromkeys(out))
h=HTML.read_text(encoding='utf-8'); eligible=arr(h,'ELIGIBLE'); grounds=arr(h,'GROUNDS'); supporting=arr(h,'LAW2_ORIGIN_LOCATIONS',False)
origins=[x.get('name') or x.get('club') for x in eligible if x.get('name') or x.get('club')]; gnames=[x.get('name') or x.get('club') for x in grounds if x.get('name') or x.get('club')]
if len(origins)!=651:raise SystemExit(f'ABORT: expected 651 Law 2 origins, found {len(origins)}')
# Every selectable origin needs either a guarded canonical ground or the explicit supporting layer.
ground_keys={ground_key(g) for g in gnames}; support_keys={ground_key(x.get('name') or x.get('club')) for x in supporting}; no_location=[n for n in origins if ground_key(n) not in ground_keys|support_keys]
if no_location:raise SystemExit(f'ABORT: Law 2 origin without selectable location: {no_location}')
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
accepted={k:v[0] for k,v in accepted_groups.items()}
def accepted_names_in_exemption_line(x):
 k=fa_key(x)
 if k in accepted:return [accepted[k]]
 for official,variants in EXEMPTION_DOCUMENT_ALIASES.items():
  if x in variants:return [official]
 pairs=[]
 for first in clubs:
  for variant in exemption_variants(first):
   if x.startswith(variant):
    rest=x[len(variant):].strip(); rk=fa_key(rest)
    if rk in accepted:pairs.append((first,accepted[rk]))
 pairs=list(dict.fromkeys(pairs))
 if len(pairs)>1:raise SystemExit(f'ABORT: ambiguous concatenated exemption line {x}: {pairs}')
 return list(pairs[0]) if pairs else []
ex_raw=pdf(EXEMPTIONS_URL); ex=[re.sub(r'\s+',' ',x).strip() for x in ex_raw.splitlines() if x.strip()]; rm={}; cur=None; headings=[]; transitions=[]
for x in ex:
 r=eround(x)
 if r:cur=r;headings.append((x,r));continue
 if epr_transition(x):cur='Extra Preliminary Round';transitions.append(x);continue
 for name in accepted_names_in_exemption_line(x):rm[fa_key(name)]=cur
if not headings:raise SystemExit('ABORT: no official exemption headings parsed')
if len(transitions)!=1:raise SystemExit(f'ABORT: expected one Step 4 Extra Preliminary transition, found {len(transitions)}')
layout='\n'.join(pdf_pages(EXEMPTIONS_URL,layout=True)); layout_norm=re.sub(r'[ \t]+',' ',layout)
m32=re.search(r'\(32\)\s*Step\s*5\s*Promoted\s*Clubs',layout_norm,re.I); m91=re.search(r'\(91\)\s*Step\s*4\s*Lowest\s*Ranked\s*\(2025-26\)',layout_norm,re.I)
if not m32 or not m91 or m91.start()<=m32.end():raise SystemExit('ABORT: Step 4 sublist markers not found in layout extraction')
block32=layout_norm[m32.end():m91.start()]; block91=layout_norm[m91.end():]
def names_in_block(block):return [c for c in clubs if any(full_name_present(v,block) for v in exemption_variants(c))]
step5_promoted=names_in_block(block32); step4_lowest=names_in_block(block91)
if len(step5_promoted)!=32 or len(step4_lowest)!=91:raise SystemExit(f'ABORT: EPR composition drift: Step5={len(step5_promoted)} Step4={len(step4_lowest)}')
for c in step5_promoted+step4_lowest:rm[fa_key(c)]='Extra Preliminary Round'
round_of={c:rm.get(fa_key(c),'Extra Preliminary Round') for c in clubs};counts={}
for c,r in round_of.items():counts[r]=counts.get(r,0)+1
expected_counts={'Extra Preliminary Round':438,'Preliminary Round':53,'First Round Qualifying':88,'Second Round Qualifying':48,'Fourth Round Qualifying':24,'First Round Proper':48,'Third Round Proper':44}
for r,n in expected_counts.items():
 if counts.get(r)!=n:raise SystemExit(f'ABORT: expected {n} entrants for {r}, got {counts.get(r)}; counts={counts}')
# Resolve all current 651 origins to official identities and require exact Law 2 membership and entry labels.
resolved=[]; rec=[]; unmatched=[]
for row in eligible:
 n=row.get('name') or row.get('club')
 if fa_key(n) in accepted:o=accepted[fa_key(n)]
 elif n in ALIASES and fa_key(ALIASES[n]) in accepted:o=accepted[fa_key(ALIASES[n])];rec.append((n,o))
 else:unmatched.append(n);continue
 resolved.append((row,o))
if unmatched:raise SystemExit(f'ABORT: unmatched Law 2 origins {unmatched}')
resolved_groups=defaultdict(list)
for row,o in resolved:resolved_groups[fa_key(o)].append(row.get('name') or row.get('club'))
merged={accepted[k]:v for k,v in resolved_groups.items() if len(v)>1}
if merged:raise SystemExit(f'ABORT: multiple origins resolve to one official identity: {merged}')
covered=set(resolved_groups); law2_official={fa_key(c) for c,r in round_of.items() if r in LAW2_ROUNDS}
if len(law2_official)!=651 or covered!=law2_official:
 missing=sorted(accepted[k] for k in law2_official-covered); extra=sorted(accepted[k] for k in covered-law2_official);raise SystemExit(f'ABORT: Law 2 identity-set mismatch; missing={missing}; extra={extra}')
label_mismatch=[]
for row,o in resolved:
 official_round=round_of[o]; stored=row.get('entry_round')
 if stored!=official_round:label_mismatch.append({'club':row.get('name'),'stored':stored,'official':official_round})
if label_mismatch:raise SystemExit('ABORT: Law 2 entry-round label mismatch: '+json.dumps(label_mismatch,ensure_ascii=False))
# The companion registry intentionally remains the 252 identities outside the original
# EPR+Preliminary baseline. 160 of these are now selectable Law 2 origins; 92 are Proper-only.
baseline={fa_key(c) for c,r in round_of.items() if r in BASELINE_ROUNDS}
if len(baseline)!=491:raise SystemExit(f'ABORT: official original baseline is {len(baseline)}, expected 491')
missing=[c for c in clubs if fa_key(c) not in baseline]
if len(missing)!=252:raise SystemExit(f'ABORT: companion registry scope is {len(missing)}, expected 252')
gby_fa=defaultdict(list);gby_relaxed=defaultdict(list);official_by_relaxed=defaultdict(list)
for n in gnames:gby_fa[fa_key(n)].append(n);gby_relaxed[ground_key(n)].append(n)
for c in clubs:official_by_relaxed[ground_key(c)].append(c)
queue=[]
for c in missing:
 exact=gby_fa.get(fa_key(c),[])
 if len(exact)>1:raise SystemExit(f'ABORT: ambiguous exact existing GROUNDS match for {c}: {exact}')
 e=None;method=None
 if exact:e=exact[0];method='fa-identity'
 else:
  relaxed=gby_relaxed.get(ground_key(c),[]);peers=official_by_relaxed.get(ground_key(c),[])
  if len(relaxed)>1:raise SystemExit(f'ABORT: ambiguous relaxed GROUNDS match for {c}: {relaxed}')
  if len(relaxed)==1 and len(peers)==1:e=relaxed[0];method='unique-ground-compatible'
 queue.append({'club':c,'entry_round':round_of[c],'existing_ground_record':e,'ground_match_method':method,'verification_status':'existing-ground-record-needs-registry-review' if e else 'pending'})
existing=sum(bool(x['existing_ground_record']) for x in queue);pending=len(queue)-existing
report={'official_accepted':743,'protected_origin_records':491,'law2_origin_records':651,'law2_origin_location_coverage':651,'reconciled_official_origin_identities':len(covered),'identity_reconciliations':[{'origin_name':a,'official_name':b} for a,b in rec],'additional_journey_clubs':252,'law2_promoted_from_companion_registry':160,'proper_round_only_companion_clubs':92,'raw_ground_records':len(gnames),'additional_clubs_with_existing_ground_record':existing,'additional_clubs_pending_ground_verification':pending,'entry_round_counts':counts,'step5_promoted_epr_clubs':len(step5_promoted),'step4_lowest_ranked_epr_clubs':len(step4_lowest),'additional_clubs':queue,'read_only':True}
(ROOT/'updater'/'fa-cup-journey-registry-audit.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'updater'/'journey-club-verification-queue.json').write_text(json.dumps({'clubs':queue},indent=2)+'\n')
md=['# FA Cup Journey Registry — Read-only reconciliation','','- Official accepted clubs: **743**','- Original EPR + Preliminary baseline: **491**','- Current Law 2 selectable origins: **651**','- Law 2 selectable origin locations: **651/651**','- Companion Journey Registry identities: **252**','- Law 2 clubs promoted from companion registry: **160**','- Proper-round-only companion identities: **92**',f'- Existing guarded GROUNDS records among companion clubs: **{existing}**',f'- Pending guarded ground promotion: **{pending}**','','## Entry-round population']+[f'- {r}: **{counts[r]}**' for r in ROUNDS if r in counts]+['','## Safety','- READ ONLY. Canonical Clubfinder, competition, grounds, mileage and journey data untouched.','- Current Clubfinder Law 2 origins must exactly equal the 651 official qualifying-round entrants.','- The companion registry remains 252 clubs outside the original 491 baseline so its evidence lifecycle remains stable.','- Proper-round-only clubs remain outside Clubfinder origin eligibility.','- The Step 4 exception is independently validated as 32 promoted Step 5 + 91 lowest-ranked Step 4 = 123 clubs.']
(ROOT/'fa-cup-journey-registry-audit.md').write_text('\n'.join(md)+'\n')
print('FA CUP JOURNEY REGISTRY AUDIT: SUCCESS');print('Current Law 2 origins:',len(covered));print('Original baseline:',len(baseline));print('Companion registry scope:',len(missing));print('Entry rounds:',counts);print('READ ONLY')