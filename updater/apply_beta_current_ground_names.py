#!/usr/bin/env python3
"""Apply and verify club-confirmed current ground details in the BETA listing or explicitly selected Public rows."""
import argparse
import json
import math
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'beta/clubfinder-beta.html'
PUBLIC = ROOT / 'clubfinder.html'
LEDGER = ROOT / 'updater/current-ground-name-ledger.json'


def literal(html, name):
    match = re.search(r'\b(?:const|let|var)\s+' + re.escape(name) + r'\s*=\s*', html)
    if not match:
        raise ValueError('Missing data literal: ' + name)
    start = match.end()
    value, size = json.JSONDecoder().raw_decode(html[start:])
    return start, start + size, value


def compact(value, *, ensure_ascii=False):
    return json.dumps(value, ensure_ascii=ensure_ascii, separators=(',', ':'))


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
        if not all(isinstance(v, str) and v.strip() == v and v for v in (before, after, postcode)):
            raise ValueError('Invalid current ground details: ' + club)
        previous_postcode = item.get('previous_postcode', postcode)
        if not isinstance(previous_postcode, str) or not re.fullmatch(r'[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}', previous_postcode):
            raise ValueError('Invalid previous postcode: ' + club)
        if not re.fullmatch(r'[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}', postcode):
            raise ValueError('Invalid reviewed postcode: ' + club)
        matches = [(store, row) for store in stores for row in store['rows'] if row.get('name') == club]
        if len(matches) != 1:
            raise ValueError('Expected one exact ground record: ' + club)
        store, row = matches[0]
        if row.get('postcode') not in (previous_postcode, postcode) or row.get('ground') not in (before, after):
            raise ValueError('Ground identity/postcode drift: ' + club)
        updated_row = dict(row, ground=after, postcode=postcode)
        if 'coordinates' in item:
            record = item['coordinates']
            prior, reviewed = (record.get(k) for k in ('previous', 'reviewed'))
            for point in (prior, reviewed):
                if (not isinstance(point, dict) or set(point) != {'lat', 'lon'}
                        or any(type(point[k]) not in (float, int) or not math.isfinite(point[k])
                               or abs(point[k]) > limit for k, limit in (('lat', 90), ('lon', 180)))):
                    raise ValueError('Invalid reviewed coordinates: ' + club)
            current = {k: row.get(k) for k in ('lat', 'lon')}
            if current not in (prior, reviewed) or not isinstance(record.get('source'), str) or not record['source'].strip():
                raise ValueError('Coordinate drift or missing coordinate evidence: ' + club)
            updated_row.update(reviewed, coordinate_source=record['source'])
        if updated_row == row:
            continue
        ascii_row = compact(row, ensure_ascii=True)
        original = compact(row)
        ensure_ascii = original != ascii_row and original not in store['body']
        if ensure_ascii:
            original = ascii_row
        if store['body'].count(original) != 1:
            raise ValueError('Ground serialization boundary changed: ' + club)
        updated = compact(updated_row, ensure_ascii=ensure_ascii)
        store['body'] = store['body'].replace(original, updated, 1)
        changes.append(club)
    for store in sorted(stores, key=lambda item: item['start'], reverse=True):
        html = html[:store['start']] + store['body'] + html[store['end']:]
    return html, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--check', action='store_true')
    parser.add_argument('--public', action='store_true', help='Use the Public listing for an explicit set of reviewed clubs')
    parser.add_argument('--club', action='append', default=[], help='Select an exact reviewed club (repeatable)')
    args = parser.parse_args()
    if args.public and not args.club:
        parser.error('--public requires explicit --club selections')
    path = PUBLIC if args.public else HTML
    ledger = json.loads(LEDGER.read_text(encoding='utf-8'))
    if args.club:
        if len(set(args.club)) != len(args.club) or not set(args.club) <= {r['club'] for r in ledger['approved']}:
            parser.error('Duplicate or unknown --club selection')
        ledger['approved'] = [r for r in ledger['approved'] if r['club'] in args.club]
    html = path.read_text(encoding='utf-8')
    expected, changes = apply_names(html, ledger)
    if args.check and expected != html:
        raise SystemExit('CURRENT GROUND NAME CHECK: FAIL — reviewed names not applied')
    if args.apply and expected != html:
        path.write_text(expected, encoding='utf-8')
    print('CURRENT GROUND NAMES: PASS', {'changes': changes, 'applied': args.apply, 'check': args.check})


if __name__ == '__main__':
    main()
