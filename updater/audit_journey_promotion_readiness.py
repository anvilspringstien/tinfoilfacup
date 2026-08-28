#!/usr/bin/env python3
"""Read-only promotion-readiness gate for Journey Club venue evidence.

The journey is authoritative. This does NOT promote or mutate canonical data.
It determines which additional clubs have evidence strong enough to be considered
for a later guarded promotion step, and keeps FCHD-only evidence explicitly out.
"""
from pathlib import Path
from collections import defaultdict
import json

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'updater'/'journey-source-of-truth-audit.json'
OUT=ROOT/'updater'/'journey-promotion-readiness-audit.json'
MD=ROOT/'journey-promotion-readiness-audit.md'

if not SRC.exists(): raise SystemExit('ABORT: journey source-of-truth audit missing')
data=json.loads(SRC.read_text(encoding='utf-8'))
clubs=data.get('clubs',[])
if len(clubs)!=252: raise SystemExit(f'ABORT: expected 252 journey clubs, found {len(clubs)}')

rows=[]
for item in clubs:
    status=item.get('journey_status')
    club=item.get('club')
    if status=='awaiting-journey-entry':
        readiness='not-yet-active'
        reason='Journey has not reached this club; no promotion permitted.'
    elif status=='journey-active-existing-guarded-ground':
        readiness='ready-existing-guarded-ground'
        reason='Already covered by a guarded GROUNDS record; actual tie venue still outranks it.'
    elif status=='journey-explicit-venue-evidence':
        readiness='ready-for-human-promotion-review'
        reason='Journey carries explicit non-FCHD venue evidence; retain provenance and review before any canonical write.'
    elif status in ('journey-active-fchd-fallback','journey-active-fchd-candidate'):
        readiness='active-supporting-evidence-only'
        reason='FCHD evidence supports the active journey but is not sufficient for verified promotion.'
    else:
        readiness='blocked-needs-evidence'
        reason='Active journey lacks acceptable venue evidence; fail closed.'
    rows.append({'club':club,'entry_round':item.get('entry_round'),'journey_status':status,'promotion_readiness':readiness,'reason':reason})

counts=defaultdict(int)
for r in rows: counts[r['promotion_readiness']]+=1
if sum(counts.values())!=252: raise SystemExit('ABORT: promotion-readiness partition does not total 252')
if counts['blocked-needs-evidence']:
    raise SystemExit(f"ABORT: {counts['blocked-needs-evidence']} journey-active clubs lack acceptable venue evidence")

report={
 'principle':'The Tin Foil FA Cup journey is the source of truth. Promotion follows journey evidence, never static candidate availability alone.',
 'additional_journey_clubs':252,
 'readiness_counts':dict(sorted(counts.items())),
 'clubs':rows,
 'read_only':True,
 'canonical_data_changed':False,
 'automatic_promotion_permitted':False
}
OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
md=['# Journey Promotion Readiness — read-only gate','',
    '**Principle:** The Tin Foil FA Cup journey is the source of truth. Promotion follows journey evidence, never static candidate availability alone.','',
    f'- Additional journey clubs: **252**','', '## Readiness']
for s,n in sorted(counts.items()): md.append(f'- {s}: **{n}**')
md += ['','## Promotion policy',
       '- Awaiting clubs are never promoted early.',
       '- Existing guarded GROUNDS records remain protected and usable.',
       '- Explicit non-FCHD journey venue evidence may enter human promotion review with provenance retained.',
       '- FCHD-only candidates/fallbacks remain supporting evidence only and are not labelled verified.',
       '- Any active club without acceptable evidence fails closed.',
       '- This audit performs no automatic promotion and no canonical writes.']
MD.write_text('\n'.join(md)+'\n',encoding='utf-8')
print('JOURNEY PROMOTION READINESS AUDIT: SUCCESS')
for s,n in sorted(counts.items()): print(s+':',n)
print('READ ONLY: automatic promotion disabled; canonical data untouched')
