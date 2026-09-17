#!/usr/bin/env python3
"""Apply verified match-specific venues to exact historical competition rows.

No venue is inferred from the home club. Sources are either an already verified
semantic fixture copy or an explicit entry in historical-match-venue-ledger.json.
Conflicting verified venues fail closed.
"""
import copy
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / 'competition.json'
LEDGER = ROOT / 'updater' / 'historical-match-venue-ledger.json'


def norm(s):
    s = str(s or '').lower().replace('&', ' and ')
    s = re.sub(r'\b(fc|afc|cfc|football club)\b', ' ', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def valid_venue(row):
    venue = row.get('venue') if isinstance(row, dict) else None
    if not isinstance(venue, dict):
        return False
    ground = str(venue.get('ground') or '').strip()
    postcode = str(venue.get('postcode') or '').strip()
    return bool((ground and 'TBC' not in ground.upper()) or (postcode and 'TBC' not in postcode.upper()))


def venue_signature(venue):
    return (
        re.sub(r'\s+', ' ', str((venue or {}).get('ground') or '').strip()).lower(),
        re.sub(r'\s+', '', str((venue or {}).get('postcode') or '').upper()),
    )


def match_key(row):
    return (
        str(row.get('round') or '').strip(),
        str(row.get('date') or '').strip(),
        norm(row.get('home')),
        norm(row.get('away')),
    )


def walk_dicts(obj, path='$', seen=None):
    if seen is None:
        seen = set()
    oid = id(obj)
    if oid in seen:
        return
    if isinstance(obj, dict):
        seen.add(oid)
        yield path, obj
        for key, value in obj.items():
            yield from walk_dicts(value, f'{path}.{key}', seen)
    elif isinstance(obj, list):
        seen.add(oid)
        for i, value in enumerate(obj):
            yield from walk_dicts(value, f'{path}[{i}]', seen)


def fixture_values(src):
    return list(src.values()) if isinstance(src, dict) else list(src or [])


def canonical_fixture_rows(data):
    rows = []
    rows.extend(fixture_values(data.get('fixtures') or {}))
    rows.extend(fixture_values(data.get('preliminary_fixtures') or {}))
    for source in (data.get('round_fixtures') or {}).values():
        rows.extend(fixture_values(source))
    return [row for row in rows if isinstance(row, dict) and row.get('home') and row.get('away')]


def main():
    data = json.loads(COMP.read_text(encoding='utf-8'))
    ledger = json.loads(LEDGER.read_text(encoding='utf-8'))
    sources = {}

    for row in canonical_fixture_rows(data):
        if not valid_venue(row):
            continue
        key = match_key(row)
        venue = copy.deepcopy(row['venue'])
        existing = sources.get(key)
        if existing and venue_signature(existing) != venue_signature(venue):
            raise SystemExit(f'ABORT: conflicting canonical fixture venues for {key}')
        sources[key] = venue

    ledger_keys = []
    for entry in ledger.get('entries', []):
        if not isinstance(entry, dict) or not entry.get('home') or not entry.get('away'):
            raise SystemExit('ABORT: malformed historical venue ledger entry')
        if not valid_venue(entry):
            raise SystemExit(f"ABORT: ledger entry lacks verified venue: {entry.get('home')} v {entry.get('away')}")
        key = match_key(entry)
        venue = copy.deepcopy(entry['venue'])
        existing = sources.get(key)
        if existing and venue_signature(existing) != venue_signature(venue):
            raise SystemExit(f'ABORT: ledger conflicts with canonical fixture venue for {key}')
        sources[key] = venue
        ledger_keys.append(key)

    rows = list(walk_dicts(data))
    changed = 0
    matched = {key: 0 for key in ledger_keys}
    conflicts = []
    for path, row in rows:
        if not isinstance(row, dict) or not row.get('home') or not row.get('away'):
            continue
        key = match_key(row)
        venue = sources.get(key)
        if not venue:
            continue
        if key in matched:
            matched[key] += 1
        if valid_venue(row):
            if venue_signature(row.get('venue')) != venue_signature(venue):
                conflicts.append(f'{path}: {row.get("home")} v {row.get("away")}')
            continue
        row['venue'] = copy.deepcopy(venue)
        changed += 1

    if conflicts:
        raise SystemExit('ABORT: conflicting historical match venue copies: ' + ' | '.join(conflicts[:20]))
    missing = [key for key, count in matched.items() if count == 0]
    if missing:
        raise SystemExit(f'ABORT: ledger match not found in competition state: {missing}')

    petts_key = ('First Round Qualifying', '2026-09-05', norm('Petts Wood & Holmesdale'), norm('Windsor & Eton'))
    anchor_rows = [row for _path, row in rows if isinstance(row, dict) and match_key(row) == petts_key]
    if not anchor_rows:
        raise SystemExit('ABORT: Petts Wood & Holmesdale v Windsor & Eton anchor not found')
    bad = [row for row in anchor_rows if venue_signature(row.get('venue')) != ('the new inn stadium', 'BR28HQ')]
    if bad:
        raise SystemExit(f'ABORT: Petts Wood historical venue did not propagate to all semantic copies ({len(bad)} bad)')

    if changed:
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        COMP.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    print('HISTORICAL MATCH VENUE PROPAGATION: PASS')
    print('Verified semantic venue sources:', len(sources))
    print('Historical copies updated:', changed)
    print('Ledger anchors matched:', sum(matched.values()))
    print('Petts Wood & Holmesdale v Windsor & Eton -> The New Inn Stadium, BR2 8HQ: PASS')
    print('Competition state changed:', 'YES' if changed else 'NO (idempotent)')


if __name__ == '__main__':
    main()
