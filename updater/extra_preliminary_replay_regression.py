#!/usr/bin/env python3
"""Guard every Extra Preliminary replay against a retained drawn first leg."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'competition.json').read_text(encoding='utf-8'))
EXPECTED_ORIGINAL_TIES = 219


def norm(s):
    s = str(s or '').lower().replace('&', ' and ')
    s = re.sub(r'\b(fc|afc|cfc|football club)\b', ' ', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


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


originals = unique_round('Extra Preliminary Round')
replays = unique_round('Extra Preliminary Round Replay')
if len(originals) != EXPECTED_ORIGINAL_TIES:
    raise SystemExit(f'EXTRA PRELIMINARY ORIGINAL COVERAGE IS NOT {EXPECTED_ORIGINAL_TIES}: {len(originals)}')

original_by_pair = {}
for row in originals:
    original_by_pair.setdefault(pair_key(row), []).append(row)

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
print('Replay records checked:', len(replays))
print('Every replay has an earlier drawn first leg: PASS')
print('Amersham 2-2 -> 1-2 chronology: PASS')
