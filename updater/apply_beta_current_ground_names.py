#!/usr/bin/env python3
"""Apply reviewed current ground-name changes to the public BETA listing only."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'beta/clubfinder-beta.html'
LEDGER = ROOT / 'updater/current-ground-name-ledger.json'


def literal(html, name):
    match = re.search(r'\b(?:const|let|var)\s+' + re.escape(name) + r'\s*=\s*', html)
    if not match:
        raise ValueError('Missing data literal: ' + name)
    start = match.end()
    value, size = json.JSONDecoder().raw_decode(html[start:])
    return start, start + size, value


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def apply_names(html, ledger):
    if ledger.get('schema_version') != 1 or not ledger.get('approved'):
        raise ValueError('Expected a nonempty reviewed name ledger')
    _, _, eligible = literal(html, 'ELIGIBLE')
    names = {row['name'] for row in eligible}
    stores = []
    for name in ('GROUNDS', 'LAW2_ORIGIN_LOCATIONS'):
        if name != 'GROUNDS' and not re.search(r'\b(?:const|let|var)\s+' + name + r'\s*=', html):
            continue
        start, end, rows = literal(html, name)
        stores.append({'start': start, 'end': end, 'rows': rows, 'body': html[start:end]})
    seen = set()
    changes = []
    for item in ledger['approved']:
        club = item.get('club')
        if club in seen or club not in names:
            raise ValueError('Duplicate or unknown club: ' + str(club))
        seen.add(club)
        if item.get('status') != 'club_confirmed' or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', item.get('reviewed_on', '')):
            raise ValueError('Missing reviewed club confirmation: ' + club)
        urls = item.get('public_sources') or []
        if not urls or any(urlparse(u).scheme != 'https' or not urlparse(u).hostname or urlparse(u).username or urlparse(u).password for u in urls):
            raise ValueError('Expected public HTTPS evidence: ' + club)
        before, after, postcode = (item.get(k) for k in ('previous_name', 'current_name', 'postcode'))
        if not all(isinstance(v, str) and v.strip() == v and v for v in (before, after, postcode)) or before == after:
            raise ValueError('Invalid name-only change: ' + club)
        matches = [(store, row) for store in stores for row in store['rows'] if row.get('name') == club]
        if len(matches) != 1:
            raise ValueError('Expected one exact ground record: ' + club)
        store, row = matches[0]
        if row.get('postcode') != postcode or row.get('ground') not in (before, after):
            raise ValueError('Ground identity/postcode drift: ' + club)
        if row['ground'] == after:
            continue
        original = compact(row)
        if store['body'].count(original) != 1:
            raise ValueError('Ground serialization boundary changed: ' + club)
        updated = dict(row, ground=after)
        store['body'] = store['body'].replace(original, compact(updated), 1)
        changes.append(club)
    for store in sorted(stores, key=lambda item: item['start'], reverse=True):
        html = html[:store['start']] + store['body'] + html[store['end']:]
    return html, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    html = HTML.read_text(encoding='utf-8')
    expected, changes = apply_names(html, json.loads(LEDGER.read_text(encoding='utf-8')))
    if args.check and expected != html:
        raise SystemExit('CURRENT GROUND NAME CHECK: FAIL — reviewed names not applied')
    if args.apply and expected != html:
        HTML.write_text(expected, encoding='utf-8')
    print('CURRENT GROUND NAMES: PASS', {'changes': changes, 'applied': args.apply, 'check': args.check})


if __name__ == '__main__':
    main()
