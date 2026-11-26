#!/usr/bin/env python3
"""Reconcile approved current Clubfinder facts from reviewed ledgers into Public."""
import argparse
import json
from pathlib import Path

from updater.apply_beta_current_ground_names import apply_names, literal
from updater.audit_active_custodian_locations import identity_key

from updater.public_club_facts_guard import reviewed_websites, render_websites, website_plan

ROOT = Path(__file__).resolve().parents[1]


def location_rows(html):
    return [row for name in ('GROUNDS', 'LAW2_ORIGIN_LOCATIONS') for row in literal(html, name)[2]]


def reconcile(root=ROOT):
    public_file = root / 'clubfinder.html'
    original = public_file.read_text(encoding='utf-8')
    beta = (root / 'beta/clubfinder-beta.html').read_text(encoding='utf-8')
    ledger = json.loads((root / 'updater/current-ground-name-ledger.json').read_text(encoding='utf-8'))
    if apply_names(beta, ledger)[1]:
        raise ValueError('The approved current listing ledger must first match BETA')
    public_map = literal(original, 'CLUB_WEBSITES')[2]
    beta_map = literal(beta, 'CLUB_WEBSITES')[2]
    public_origins = [row['name'] for row in literal(original, 'ELIGIBLE')[2]]
    beta_origins = [row['name'] for row in literal(beta, 'ELIGIBLE')[2]]
    if any(len(set(names)) != len(names) for names in (public_origins, beta_origins)):
        raise ValueError('Duplicate eligible identities')
    ready, held = website_plan(public_map, beta_map, reviewed_websites(root))
    website_source = original
    if ready:
        website_source = render_websites(root, original, [row for row, _ in ready])
    candidate, changed = apply_names(website_source, ledger)
    current_locations = {row['name']: row for row in location_rows(original)}
    resulting_locations = {row['name']: row for row in location_rows(candidate)}
    public_location_ids = {identity_key(name) for name in current_locations}
    pending = [
        {'club': row['name'], 'ground': row['ground'], 'postcode': row['postcode'], 'source': row['source']}
        for row in location_rows(beta)
        if row.get('preview_evidence_only') and identity_key(row['name']) not in public_location_ids
    ]

    def coverage(names, site_map):
        return {'eligible': len(names), 'linked': sum(bool(site_map.get(name)) for name in names)}

    report = {
        'public_before': coverage(public_origins, public_map),
        'public_after': coverage(public_origins, literal(candidate, 'CLUB_WEBSITES')[2]),
        'beta': coverage(beta_origins, beta_map),
        'eligible_only_in_public': sorted(set(public_origins) - set(beta_origins)),
        'eligible_only_in_beta': sorted(set(beta_origins) - set(public_origins)),
        'approved_website_additions': [
            {'identity': row['club'], 'url': row['url'], 'verified_on': row['verified_on'], 'ledger': source}
            for row, source in ready
        ],
        'held_website_differences': held,
        'approved_ground_changes': [
            {'club': name, **{
                field: {'previous': current_locations[name].get(field), 'reviewed': resulting_locations[name].get(field)}
                for field in ('ground', 'postcode', 'lat', 'lon')
                if current_locations[name].get(field) != resulting_locations[name].get(field)
            }}
            for name in changed
        ],
        'pending_entrant_ground_evidence': sorted(pending, key=lambda row: row['club']),
    }
    return original, candidate, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    original, candidate, report = reconcile()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.check and original != candidate:
        raise SystemExit('Public Clubfinder differs from approved current facts')
    if args.apply and original != candidate:
        (ROOT / 'clubfinder.html').write_text(candidate, encoding='utf-8')


if __name__ == '__main__':
    main()
