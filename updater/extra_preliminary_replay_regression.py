#!/usr/bin/env python3
"""Guard every Extra Preliminary replay against a retained original tie."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'competition.json').read_text(encoding='utf-8'))
EXPECTED_ORIGINAL_TIES = 219

# Keep identity matching aligned with sync_extra_preliminary_chronology.py.
# These are matching aliases only; display/stored club names are untouched.
TEAM_IDENTITY_ALIASES = {
    'bedfont sports club': 'bedfont sports',
    'bournemouth poppies': 'bournemouth',
    'atherton lr': 'atherton laburnum rovers',
    'irlam': 'irlam town',
    'eastwood community': 'eastwood',
    'millbrook hampshire': 'millbrook',
    'royal wootton bassett town': 'royal wootton bassett',
    'sherbourne town': 'sherborne town',
    'sutton united birmingham': 'sutton united west midlands',
    'varndeanians': 'varndenians',
}


def norm(s):
    s = str(s or '').lower().replace('&', ' and ')
    s = re.sub(r'\b(fc|afc|cfc|football club)\b', ' ', s)
    s = re.sub(r'[^a-z0-9]+', ' ', s).strip()
    return TEAM_IDENTITY_ALIASES.get(s, s)


def semantic_key(row):
    return (
        norm(row.get('home')),
        norm(row.get('away')),
        str(row.get('date') or ''),
        row.get('home_score'),
        row.get('away_score'),
    )


def unique_round(round_name):
    out = {}
    for arr in (DATA.get('result_history') or {}).values():
        if not isinstance(arr, list):
            continue
        for row in arr:
            if isinstance(row, dict) and row.get('round') == round_name:
                out.setdefault(semantic_key(row), row)
    return list(out.values())


def pair_key(row):
    return frozenset((norm(row.get('home')), norm(row.get('away'))))


def row_label(row):
    hs, ass = row.get('home_score'), row.get('away_score')
    score = f'{hs}-{ass}' if hs is not None and ass is not None else str(row.get('status') or row.get('decision') or 'no-score')
    return f"{row.get('date')}: {row.get('home')} {score} {row.get('away')}"


originals = unique_round('Extra Preliminary Round')
replays = unique_round('Extra Preliminary Round Replay')
if len(originals) != EXPECTED_ORIGINAL_TIES:
    raise SystemExit(f'EXTRA PRELIMINARY ORIGINAL COVERAGE IS NOT {EXPECTED_ORIGINAL_TIES}: {len(originals)}')

original_by_pair = {}
for row in originals:
    original_by_pair.setdefault(pair_key(row), []).append(row)

# A 219-row chronology is only valid if it also represents the FA's 219
# distinct draw ties. This catches a duplicate result row masquerading as a
# missing original tie before replay ancestry is assessed.
duplicate_pairs = {pair: rows for pair, rows in original_by_pair.items() if len(rows) > 1}
if len(original_by_pair) != EXPECTED_ORIGINAL_TIES:
    lines = [f'EXTRA PRELIMINARY DISTINCT DRAW-PAIR COVERAGE IS {len(original_by_pair)}; expected {EXPECTED_ORIGINAL_TIES}.']
    if duplicate_pairs:
        lines.append('DUPLICATE ORIGINAL PAIR(S):')
        for rows in duplicate_pairs.values():
            lines.extend('  ' + row_label(row) for row in rows)
    raise SystemExit('\n'.join(lines))

# Aylesbury United v Flackwell Heath is the known abandoned/rearranged edge
# case. The 7 August match was abandoned; the completed 12 August 2-3 fixture
# is therefore the original tie, not a replay. Keep this explicit so a source
# label cannot silently recreate false replay ancestry.
aylesbury_pair = frozenset((norm('Aylesbury United'), norm('Flackwell Heath')))
aylesbury_original = [
    row for row in originals
    if pair_key(row) == aylesbury_pair
    and str(row.get('date') or '') == '2026-08-12'
    and row.get('home_score') == 2
    and row.get('away_score') == 3
    and norm(row.get('home')) == norm('Aylesbury United')
    and norm(row.get('away')) == norm('Flackwell Heath')
]
aylesbury_replay = [row for row in replays if pair_key(row) == aylesbury_pair]
if len(aylesbury_original) != 1 or aylesbury_replay:
    raise SystemExit(
        'AYLESBURY-FLACKWELL ABANDONED/REARRANGED REGRESSION FAILED: '
        f'originals={[row_label(row) for row in aylesbury_original]} '
        f'replays={[row_label(row) for row in aylesbury_replay]}'
    )

missing = []
not_drawn = []
for replay in replays:
    earlier = [row for row in original_by_pair.get(pair_key(replay), [])
               if str(row.get('date') or '') < str(replay.get('date') or '')]
    if not earlier:
        missing.append(f"{replay.get('home')} v {replay.get('away')} ({replay.get('date')})")
        continue
    if not any(row.get('home_score') == row.get('away_score') for row in earlier):
        not_drawn.append(f"{replay.get('home')} v {replay.get('away')} ({replay.get('date')})")

if missing:
    raise SystemExit('REPLAY(S) WITHOUT ORIGINAL EXTRA PRELIMINARY TIE: ' + ' | '.join(missing[:20]))
if not_drawn:
    raise SystemExit('REPLAY(S) WHOSE ORIGINAL TIE IS NOT DRAWN: ' + ' | '.join(not_drawn[:20]))

amersham_original = [r for r in originals
                     if norm(r.get('home')) == norm('North Leigh')
                     and norm(r.get('away')) == norm('Amersham Town')
                     and r.get('home_score') == 2 and r.get('away_score') == 2]
amersham_replay = [r for r in replays
                   if norm(r.get('home')) == norm('Amersham Town')
                   and norm(r.get('away')) == norm('North Leigh')
                   and r.get('home_score') == 1 and r.get('away_score') == 2]
if len(amersham_original) != 1 or len(amersham_replay) != 1:
    raise SystemExit('AMERSHAM EXTRA PRELIMINARY DRAW/REPLAY REGRESSION FAILED')

print('EXTRA PRELIMINARY REPLAY REGRESSION: PASS')
print('Original ties retained:', len(originals))
print('Distinct draw pairs retained:', len(original_by_pair))
print('Replay records checked:', len(replays))
print('Every replay has an earlier drawn first leg: PASS')
print('Aylesbury abandoned -> rearranged original chronology: PASS')
print('Amersham 2-2 -> 1-2 chronology: PASS')
