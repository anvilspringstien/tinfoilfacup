#!/usr/bin/env python3
"""Read-only audit: compare legacy EPR_RESULTS_BY_TIE rows with canonical competition.json.

The goal is to determine whether the legacy early-round results table contains
facts not yet represented in canonical competition data. No production file is
modified.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'clubfinder.html').read_text(encoding='utf-8')
COMP = json.loads((ROOT / 'competition.json').read_text(encoding='utf-8'))


def extract_object(name: str):
    m = re.search(r'\bconst\s+' + re.escape(name) + r'\s*=', HTML)
    if not m:
        raise SystemExit(f'EPR COVERAGE AUDIT: FAIL - {name} declaration not found')
    i = m.end()
    while i < len(HTML) and HTML[i].isspace():
        i += 1
    if i >= len(HTML) or HTML[i] != '{':
        raise SystemExit(f'EPR COVERAGE AUDIT: FAIL - {name} is not an object literal')
    depth = 0
    quote = None
    esc = False
    j = i
    while j < len(HTML):
        ch = HTML[j]
        if quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
        else:
            if ch in "'\"`":
                quote = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    raw = HTML[i:j+1]
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError as exc:
                        raise SystemExit(f'EPR COVERAGE AUDIT: FAIL - {name} is not strict JSON: {exc}')
        j += 1
    raise SystemExit(f'EPR COVERAGE AUDIT: FAIL - unbalanced {name}')


def norm(v):
    s = str(v or '').lower().strip()
    s = s.replace('&', ' and ')
    s = re.sub(r'\b(afc|fc)\b', ' ', s)
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return ' '.join(s.split())


def resultish(o):
    return isinstance(o, dict) and o.get('home') and o.get('away') and o.get('home_score') is not None and o.get('away_score') is not None


def walk(o, path='root'):
    if isinstance(o, dict):
        if resultish(o):
            yield path, o
        for k, v in o.items():
            yield from walk(v, f'{path}.{k}')
    elif isinstance(o, list):
        for idx, v in enumerate(o):
            yield from walk(v, f'{path}[{idx}]')


def sig(o):
    return (
        norm(o.get('home')),
        norm(o.get('away')),
        int(o.get('home_score')),
        int(o.get('away_score')),
    )


def round_norm(v):
    s = norm(v)
    return s.replace('extra preliminary round', 'extra preliminary').replace('preliminary round', 'preliminary')


def flatten_epr(obj):
    rows = []
    for key, value in obj.items():
        if resultish(value):
            rows.append((str(key), value))
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                if resultish(item):
                    rows.append((f'{key}[{idx}]', item))
        elif isinstance(value, dict):
            found = False
            for subk, item in value.items():
                if resultish(item):
                    rows.append((f'{key}.{subk}', item)); found = True
            if not found:
                # Ignore metadata-only branches; this is an audit, not a transformer.
                pass
    return rows


epr = extract_object('EPR_RESULTS_BY_TIE')
epr_rows = flatten_epr(epr)
canonical_rows = list(walk(COMP))
by_sig = {}
for path, row in canonical_rows:
    by_sig.setdefault(sig(row), []).append((path, row))

exact = []
near = []
missing = []
for key, row in epr_rows:
    matches = by_sig.get(sig(row), [])
    if not matches:
        missing.append((key, row))
        continue
    # Prefer same date and compatible round where present.
    same_date = [(p, r) for p, r in matches if (not row.get('date') or not r.get('date') or str(row.get('date')) == str(r.get('date')))]
    candidates = same_date or matches
    same_round = [(p, r) for p, r in candidates if (not row.get('round') or not r.get('round') or round_norm(row.get('round')) == round_norm(r.get('round')))]
    if same_round:
        exact.append((key, row, same_round[0]))
    else:
        near.append((key, row, candidates[0]))

print('EPR CANONICAL COVERAGE AUDIT')
print('Legacy EPR result rows:', len(epr_rows))
print('Canonical result-like rows scanned:', len(canonical_rows))
print('Exact/compatible canonical matches:', len(exact))
print('Scoreline/team matches with date/round mismatch:', len(near))
print('Missing from canonical competition data:', len(missing))

if near:
    print('\nMISMATCHED METADATA:')
    for key, row, (path, canon) in near[:50]:
        print(f'- {key}: {row.get("home")} {row.get("home_score")}-{row.get("away_score")} {row.get("away")} | legacy {row.get("round")} {row.get("date")} | canonical {canon.get("round")} {canon.get("date")} @ {path}')

if missing:
    print('\nMISSING CANONICAL RESULTS:')
    for key, row in missing[:100]:
        print(f'- {key}: {row.get("home")} {row.get("home_score")}-{row.get("away_score")} {row.get("away")} | {row.get("round")} | {row.get("date")} | winner={row.get("winner")}')

# Highlight the known regression sentinel explicitly.
sentinel = [row for key, row in epr_rows if norm(row.get('home')) == norm('Newton Aycliffe') and norm(row.get('away')) == norm('Kendal Town') and int(row.get('home_score')) == 0 and int(row.get('away_score')) == 1]
print('\nNewton Aycliffe 0-1 Kendal present in legacy EPR:', 'YES' if sentinel else 'NO')
if sentinel:
    print('Newton Aycliffe 0-1 Kendal present canonically:', 'YES' if by_sig.get(sig(sentinel[0])) else 'NO')

print('\nREAD ONLY. No production data changed.')
