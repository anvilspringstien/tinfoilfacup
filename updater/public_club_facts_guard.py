#!/usr/bin/env python3
"""Prove Public Clubfinder changes are exactly reviewed factual field updates."""
import argparse
from datetime import date
import json
from pathlib import Path
import subprocess

from updater.apply_beta_current_ground_names import apply_names, literal

ROOT = Path(__file__).resolve().parents[1]
SECURITY_HOLD = 'owner_observed_security_warning'
WEBSITE_SECTIONS = {
    'verified': {'verified_official_club_site'},
    'withdrawn': {'club_confirmed_offline', SECURITY_HOLD},
}


# The same canonical website validator and renderer used for individual batches.
WEBSITE_PUBLICATION = """
const fs = require('node:fs');
const {promote, applyMapping} = require('./updater/club_website_bulk_promote');
const competition = JSON.parse(fs.readFileSync('competition.json', 'utf8'));
const {source, ledger} = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(applyMapping(source, promote(source, competition, ledger).websites));
"""


def reviewed_websites(root):
    latest = {}
    for path in sorted((root / 'updater').glob('club_website_verified_batch_*.json')):
        ledger = json.loads(path.read_text(encoding='utf-8'))
        if ledger.get('schema_version') != 1:
            raise ValueError(f'Unsupported website evidence ledger: {path.name}')
        for section, statuses in WEBSITE_SECTIONS.items():
            for item in ledger.get(section, []):
                status = item['status']
                if status not in statuses:
                    continue
                checked = item.get('verified_on') or ledger.get('verified_on')
                checked_date = date.fromisoformat(checked)
                for name in (item['club'], *item.get('aliases', [])):
                    key = (status == SECURITY_HOLD, checked_date, path.name)
                    if name not in latest or key > latest[name][0]:
                        latest[name] = (key, {
                            'club': name, 'status': status, 'url': item['url'],
                            'evidence_url': item['evidence_url'], 'verified_on': checked,
                            **({'reason': item['reason']} if status == SECURITY_HOLD else {}),
                        }, path.name)
    return {name: (row, path) for name, (_, row, path) in latest.items()}


def website_plan(public_map, beta_map, evidence):
    ready, held = [], []
    for name, url in sorted(beta_map.items()):
        public_url = public_map.get(name)
        if public_url == url:
            continue
        row, source = evidence.get(name, ({}, None))
        if public_url:
            reason = 'conflicting_public_mapping'
        elif row.get('status') != 'verified_official_club_site' or row.get('url') != url:
            reason = 'missing_current_approval'
        else:
            ready.append((row, source))
            continue
        held.append({'identity': name, 'beta': url, 'public': public_url, 'reason': reason})
    return ready, held


def render_websites(root, original, rows, withdrawals=()):
    try:
        result = subprocess.run(
            ['node', '-e', WEBSITE_PUBLICATION], cwd=root, text=True, check=True, capture_output=True,
            input=json.dumps({'source': original, 'ledger': {'schema_version': 1, 'verified': rows, 'withdrawn': withdrawals}}),
        )
    except subprocess.CalledProcessError as error:
        raise ValueError('Canonical website publication rejected the proposed links: ' + error.stderr.strip()) from error
    return result.stdout


def prove(root, original, proposed, beta, ground_ledger, website_evidence):
    if proposed == original:
        return 0, 0
    before_map, after_map, beta_map = (literal(html, 'CLUB_WEBSITES')[2] for html in (original, proposed, beta))
    removed_names = set(before_map) - set(after_map)
    withdrawals = []
    for name in sorted(removed_names):
        review, _ = website_evidence.get(name, ({}, None))
        if review.get('status') != SECURITY_HOLD or review.get('url') != before_map[name] or name in beta_map:
            raise ValueError('Public website replacement or removal requires separate review')
        withdrawals.append(review)
    if any(after_map[name] != before_map[name] for name in before_map.keys() & after_map.keys()):
        raise ValueError('Public website replacement or removal requires separate review')
    if any(row.get('status') == SECURITY_HOLD and name in after_map
           for name, (row, _) in website_evidence.items()):
        raise ValueError('Public website retains a mapping subject to an active website warning')
    new_names = set(after_map) - set(before_map)
    allowed, _ = website_plan(before_map, beta_map, website_evidence)
    by_name = {item['club']: item for item, _ in allowed}
    if any(name not in by_name or by_name[name]['url'] != after_map[name] for name in new_names):
        raise ValueError('Public website changes lack exact approved BETA evidence')
    expected = (render_websites(root, original, [by_name[name] for name in sorted(new_names)], withdrawals)
                if new_names or withdrawals else original)

    selected = set()
    for table in ('GROUNDS', 'LAW2_ORIGIN_LOCATIONS'):
        old, new = (literal(html, table)[2] for html in (original, proposed))
        if [row['name'] for row in old] != [row['name'] for row in new]:
            raise ValueError('Public location population or ordering changed')
        selected.update(before['name'] for before, after in zip(old, new) if before != after)
    if selected:
        rows = [row for row in ground_ledger['approved'] if row['club'] in selected]
        if {row['club'] for row in rows} != selected:
            raise ValueError('Public ground changes lack exact reviewed evidence')
        reviewed = {**ground_ledger, 'approved': rows}
        if apply_names(beta, reviewed)[1]:
            raise ValueError('Public ground changes lack matching BETA records')
        expected, _ = apply_names(expected, reviewed)
    if expected != proposed:
        raise ValueError('Public changes exceed the exact output of the approved club factual CLIs')
    return len(selected), len(new_names) + len(removed_names)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, help='Git base reference used to compare the Public file')
    args = parser.parse_args()
    base = subprocess.check_output(['git', 'merge-base', args.base, 'HEAD'], cwd=ROOT, text=True).strip()
    original = subprocess.check_output(['git', 'show', base + ':clubfinder.html'], cwd=ROOT).decode()
    proposed = (ROOT / 'clubfinder.html').read_text(encoding='utf-8')
    beta = (ROOT / 'beta/clubfinder-beta.html').read_text(encoding='utf-8')
    ledger = json.loads((ROOT / 'updater/current-ground-name-ledger.json').read_text(encoding='utf-8'))
    ground, websites = prove(ROOT, original, proposed, beta, ledger, reviewed_websites(ROOT))
    print(f'Public factual boundary: PASS ({ground} location records, {websites} website mapping keys)')


if __name__ == '__main__':
    main()
