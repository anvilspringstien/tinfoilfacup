#!/usr/bin/env python3
"""Read-only Journey-source verification audit.

The Tin Foil FA Cup journey is authoritative for *when* a club/venue matters.
This audit therefore never bulk-promotes the 252 additional clubs merely because
FCHD has a unique candidate. It activates verification only when a club appears
in the competition journey and records the strongest venue evidence carried by
that journey. FCHD remains fallback candidate evidence.
"""
from pathlib import Path
from collections import defaultdict
import json,re

ROOT=Path(__file__).resolve().parents[1]
COVER=ROOT/'updater'/'journey-ground-coverage-audit.json'
COMP=ROOT/'competition.json'
OUT=ROOT/'updater'/'journey-source-of-truth-audit.json'
MD=ROOT/'journey-source-of-truth-audit.md'

def key(s):
 s=str(s or '').lower().replace('&',' and ')
 s=re.sub(r'\b(association football club|football club)\b',' ',s)
 s=re.sub(r'[^a-z0-9]+',' ',s).strip()
 s=re.sub(r'\b(fc|cfc)\b',' ',s);s=re.sub(r'\bafc$',' ',s)
 return re.sub(r'\s+',' ',s).strip()

def fixture_rows(comp):
 out=[]
 for bucket in ('preliminary_fixtures','fixtures','replays'):
  data=comp.get(bucket,{}) or {}
  vals=list(data.values()) if isinstance(data,dict) else list(data)
  for f in vals:
   if isinstance(f,dict):out.append((bucket,f))
 return out

if not COVER.exists():raise SystemExit('ABORT: journey ground coverage audit missing')
coverage=json.loads(COVER.read_text(encoding='utf-8'))
results=coverage.get('results',[])
if len(results)!=252:raise SystemExit(f'ABORT: expected 252 additional journey clubs, found {len(results)}')
comp=json.loads(COMP.read_text(encoding='utf-8'))
rows=fixture_rows(comp)
seen=defaultdict(list)
for bucket,f in rows:
 for side in ('home','away'):
  n=f.get(side)
  if n:seen[key(n)].append((bucket,side,f))

out=[]
for item in results:
 club=item['club']; appearances=seen.get(key(club),[])
 journey=[]
 for bucket,side,f in appearances:
  v=f.get('venue') or {}
  journey.append({'bucket':bucket,'round':f.get('round'),'date':f.get('date'),'home':f.get('home'),'away':f.get('away'),'side':side,
                  'venue':v if isinstance(v,dict) else {},'venue_source':v.get('source') if isinstance(v,dict) else None,
                  'venue_verification':v.get('verification') if isinstance(v,dict) else None})
 existing=item.get('existing_ground_record')
 fchd=item.get('fchd_candidates') or []
 if not appearances:
  status='awaiting-journey-entry'
  decision='Do not promote. Candidate evidence waits until the journey reaches this club.'
 elif existing:
  status='journey-active-existing-guarded-ground'
  decision='Use the guarded ground unless the actual tie carries an explicit different venue.'
 else:
  explicit=[j for j in journey if j['venue'].get('postcode') and 'tbc' not in str(j['venue'].get('postcode')).lower()]
  independent=[j for j in explicit if 'fchd' not in str(j.get('venue_source') or '').lower() and 'fchd' not in str(j.get('venue_verification') or '').lower()]
  if independent:
   status='journey-explicit-venue-evidence'
   decision='Journey venue is authoritative for this tie; retain provenance and review before registry promotion.'
  elif explicit:
   status='journey-active-fchd-fallback'
   decision='Journey is active, but venue provenance is still FCHD fallback; do not call it independently verified.'
  elif fchd:
   status='journey-active-fchd-candidate'
   decision='Journey is active; FCHD candidate may be used as fallback evidence, pending stronger tie/club evidence.'
  else:
   status='journey-active-needs-venue-evidence'
   decision='Journey is active and no usable venue evidence exists; fail closed for venue verification.'
 out.append({**item,'journey_appearances':journey,'journey_status':status,'decision':decision})

counts=defaultdict(int)
for x in out:counts[x['journey_status']]+=1
if sum(counts.values())!=252:raise SystemExit('ABORT: journey-source partition does not total 252')
report={'principle':'The Tin Foil FA Cup journey is the source of truth. Static ground sources are supporting evidence, not authority over an actual tie venue.',
        'additional_journey_clubs':252,'competition_fixture_rows_examined':len(rows),'status_counts':dict(sorted(counts.items())),
        'clubs':out,'read_only':True,'canonical_data_changed':False}
OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
md=['# Journey Source of Truth — read-only verification audit','',
    '**Principle:** The Tin Foil FA Cup journey is the source of truth. Static ground data supports the journey; it does not override the venue of an actual tie.','',
    f'- Additional journey clubs: **252**',f'- Competition fixture/replay rows examined: **{len(rows)}**','', '## Status']
for s,n in sorted(counts.items()):md.append(f'- {s}: **{n}**')
md += ['','## Rules','- A club not yet reached by the journey is not promoted merely because FCHD has a unique candidate.',
       '- An explicit venue carried by the actual journey/tie outranks a static home-ground candidate.',
       '- FCHD-labelled venue data remains fallback evidence and is never mislabelled as independent journey verification.',
       '- Existing guarded GROUNDS records remain protected; an explicit different tie venue applies to that tie rather than silently rewriting the club home ground.',
       '- Any journey-active club with no usable venue evidence remains unresolved/fail-closed.','',
       '## Safety','- READ ONLY. Clubfinder, competition, GROUNDS, mileage and journey logic are untouched.']
MD.write_text('\n'.join(md)+'\n',encoding='utf-8')
print('JOURNEY SOURCE OF TRUTH AUDIT: SUCCESS')
print('Fixture/replay rows examined:',len(rows))
for s,n in sorted(counts.items()):print(s+':',n)
print('READ ONLY: canonical data untouched')
