#!/usr/bin/env python3
"""Build the canonical companion Journey Club Registry.

This registry contains the 252 official FA Cup identities outside the protected
491 origin-club population. The journey is the source of truth: registry
identity may be canonical, while venue evidence matures only when the journey
reaches a club. This script never edits clubfinder.html, competition.json or the
protected GROUNDS array.
"""
from pathlib import Path
from collections import Counter
import json

ROOT = Path(__file__).resolve().parents[1]
COVER = ROOT / 'updater' / 'journey-ground-coverage-audit.json'
SOURCE = ROOT / 'updater' / 'journey-source-of-truth-audit.json'
READY = ROOT / 'updater' / 'journey-promotion-readiness-audit.json'
OUT = ROOT / 'journey-club-registry.json'

for p in (COVER, SOURCE, READY):
    if not p.exists():
        raise SystemExit(f'ABORT: required gate output missing: {p.relative_to(ROOT)}')

coverage = json.loads(COVER.read_text(encoding='utf-8'))
source = json.loads(SOURCE.read_text(encoding='utf-8'))
ready = json.loads(READY.read_text(encoding='utf-8'))

cover_rows = coverage.get('results', [])
source_rows = source.get('clubs', [])
ready_rows = ready.get('clubs', [])
if not (len(cover_rows) == len(source_rows) == len(ready_rows) == 252):
    raise SystemExit('ABORT: expected 252 rows from every Journey Registry gate')

by_cover = {x['club']: x for x in cover_rows}
by_source = {x['club']: x for x in source_rows}
by_ready = {x['club']: x for x in ready_rows}
if not (set(by_cover) == set(by_source) == set(by_ready)):
    raise SystemExit('ABORT: Journey Registry gate identity sets disagree')

clubs = []
for club in sorted(by_source, key=str.casefold):
    c = by_cover[club]
    s = by_source[club]
    r = by_ready[club]
    if c.get('entry_round') != s.get('entry_round') or s.get('entry_round') != r.get('entry_round'):
        raise SystemExit(f'ABORT: entry-round disagreement for {club}')

    appearances = s.get('journey_appearances') or []
    explicit_venues = []
    for a in appearances:
        v = a.get('venue') or {}
        if v.get('postcode') and 'tbc' not in str(v.get('postcode')).lower():
            explicit_venues.append({
                'round': a.get('round'),
                'date': a.get('date'),
                'home': a.get('home'),
                'away': a.get('away'),
                'ground': v.get('ground') or v.get('name'),
                'postcode': v.get('postcode'),
                'source': a.get('venue_source'),
                'verification': a.get('venue_verification'),
            })

    fchd_candidates = c.get('fchd_candidates') or []
    supporting = []
    for x in fchd_candidates:
        supporting.append({
            'type': 'fchd-gazetteer-candidate',
            'club_name': x.get('club'),
            'ground': x.get('ground'),
            'postcode': x.get('postcode'),
            'source': x.get('source'),
        })

    existing = c.get('existing_ground_record')
    lifecycle = r.get('promotion_readiness')
    if lifecycle == 'ready-existing-guarded-ground':
        registry_state = 'active-guarded'
    elif lifecycle == 'ready-for-human-promotion-review':
        registry_state = 'active-reviewable-journey-evidence'
    elif lifecycle == 'active-supporting-evidence-only':
        registry_state = 'active-supporting-evidence'
    elif lifecycle == 'not-yet-active':
        registry_state = 'awaiting-journey-entry'
    else:
        registry_state = 'blocked'

    clubs.append({
        'club': club,
        'entry_round': c.get('entry_round'),
        'registry_state': registry_state,
        'journey_status': s.get('journey_status'),
        'promotion_readiness': lifecycle,
        'existing_guarded_ground_record': existing,
        'ground_match_method': c.get('ground_match_method'),
        'journey_venue_evidence': explicit_venues,
        'supporting_ground_evidence': supporting,
    })

states = Counter(x['registry_state'] for x in clubs)
if states.get('blocked', 0):
    raise SystemExit(f"ABORT: {states['blocked']} Journey Registry identities are blocked")
if len(clubs) != 252:
    raise SystemExit('ABORT: Journey Club Registry does not contain exactly 252 clubs')

registry = {
    'schema_version': 1,
    'season': '2026-27',
    'competition': 'The Emirates FA Cup',
    'principle': 'The Tin Foil FA Cup journey is the source of truth. Static ground data supports the journey and never overrides the venue of an actual tie.',
    'scope': {
        'official_accepted_clubs': 743,
        'protected_origin_clubs': 491,
        'journey_registry_clubs': 252,
    },
    'safety': {
        'protected_origin_grounds_untouched': True,
        'automatic_ground_verification_from_fchd': False,
        'actual_tie_venue_overrides_static_home_ground_for_that_tie': True,
        'identity_registry_is_canonical_companion_only': True,
    },
    'state_counts': dict(sorted(states.items())),
    'clubs': clubs,
}
OUT.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('JOURNEY CLUB REGISTRY BUILD: SUCCESS')
print('Registry clubs:', len(clubs))
for k, v in sorted(states.items()):
    print(f'{k}: {v}')
print('Protected origin GROUNDS: UNTOUCHED')
