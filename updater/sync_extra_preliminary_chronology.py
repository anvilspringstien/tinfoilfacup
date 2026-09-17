#!/usr/bin/env python3
"""Restore the complete 2026-27 FA Cup Extra Preliminary Round chronology.

Football Web Pages date pages are used because the round-summary page no longer
exposes the completed round. The write is fail-closed: all 219 original ties must
be parsed before competition.json is touched. Existing later results/replays are
preserved and remain the latest result for each club.
"""
import json
import re
import urllib.request
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / 'competition.json'
BASE = 'https://www.footballwebpages.co.uk/fa-cup'
RESULT_DATES = ('20260807', '20260808', '20260809')
EXPECTED_TIES = 219
UA = 'TinFoilFACupExtraPreliminaryChronology/1.0 (+https://anvilspringstien.github.io/tinfoilfacup/)'
PROBE_ANCHORS = {'20260807': 'Ascot United', '20260808': 'North Leigh', '20260809': 'Beverley Town'}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.buf = []
        self.events = []
        self.row = []
        self.cell = None

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
        if tag in ('h2', 'h3', 'h4'):
            self.buf = []
        if tag == 'tr':
            self.row = []
        if tag in ('td', 'th'):
            self.cell = []

    def handle_data(self, data):
        if self.stack and self.stack[-1] in ('h2', 'h3', 'h4'):
            self.buf.append(data)
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            txt = ' '.join(''.join(self.cell).split())
            self.row.append(unescape(txt))
            self.cell = None
        if tag == 'tr' and self.row:
            self.events.append(('row', self.row))
            self.row = []
        if tag in ('h2', 'h3', 'h4'):
            txt = ' '.join(''.join(self.buf).split())
            if txt:
                self.events.append(('heading', unescape(txt)))
            self.buf = []
        if self.stack:
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i] == tag:
                    self.stack = self.stack[:i]
                    break


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml'})
    with urllib.request.urlopen(req, timeout=40) as response:
        return response.read().decode('utf-8', 'replace')


def norm(s):
    s = str(s or '').lower().replace('&', ' and ')
    s = re.sub(r'\b(fc|afc|cfc|football club)\b', ' ', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def aliases(name):
    suffix = re.compile(r'\s+(FC|AFC|CFC)$', re.I)
    out = {name, suffix.sub('', name)}
    if not suffix.search(name):
        out |= {name + ' FC', name + ' AFC'}
    return {x for x in out if x}


def score_int(value):
    value = str(value or '').strip()
    return int(value) if re.fullmatch(r'\d+', value) else None


def parse_results(raw, url, date):
    parser = PageParser()
    parser.feed(raw)
    out = []
    for kind, value in parser.events:
        if kind != 'row':
            continue
        cells = [c.strip() for c in value if c.strip()]
        if len(cells) < 5 or not cells[0].upper().startswith('FT'):
            continue
        hs, away_score = score_int(cells[2]), score_int(cells[3])
        if hs is None or away_score is None:
            continue
        home, away = cells[1], cells[4]
        winner = home if hs > away_score else away if away_score > hs else ''
        out.append({
            'round': 'Extra Preliminary Round',
            'date': date,
            'home': home,
            'away': away,
            'home_score': hs,
            'away_score': away_score,
            'winner': winner,
            'status': 'FT',
            'decision': '' if winner else 'draw-replay',
            'source_url': url,
        })
    return out


def source_probe(raw, compact):
    anchor = PROBE_ANCHORS.get(compact, '')
    idx = raw.lower().find(anchor.lower()) if anchor else -1
    lo = max(0, idx - 600) if idx >= 0 else 0
    hi = min(len(raw), idx + 1200) if idx >= 0 else min(len(raw), 1800)
    snippet = re.sub(r'\s+', ' ', raw[lo:hi])
    print(f'SOURCE PROBE {compact}: bytes={len(raw)} tr={raw.lower().count("<tr")} td={raw.lower().count("<td")} FT={len(re.findall(r"\\bFT\\b", raw, re.I))} anchor={anchor!r} index={idx}')
    print('SOURCE PROBE SNIPPET:', snippet)


def semantic_key(row):
    return (
        norm(row.get('home')),
        norm(row.get('away')),
        str(row.get('date') or ''),
        row.get('home_score'),
        row.get('away_score'),
    )


def same_result(a, b):
    return semantic_key(a) == semantic_key(b)


def round_order(row):
    name = str(row.get('round') or '')
    replay = 1 if name.endswith(' Replay') else 0
    return (str(row.get('date') or ''), replay)


def add_result(data, row):
    results = data.setdefault('results', {})
    history = data.setdefault('result_history', {})
    changed = False
    for club in aliases(row['home']) | aliases(row['away']):
        arr = history.setdefault(club, [])
        if not any(isinstance(existing, dict) and same_result(existing, row) for existing in arr):
            arr.append(dict(row))
            changed = True
        arr.sort(key=round_order)
        if arr:
            latest = arr[-1]
            if results.get(club) != latest:
                results[club] = latest
                changed = True
    return changed


def unique_round_rows(data, round_name):
    found = {}
    for arr in (data.get('result_history') or {}).values():
        if not isinstance(arr, list):
            continue
        for row in arr:
            if isinstance(row, dict) and row.get('round') == round_name:
                found.setdefault(semantic_key(row), row)
    return found


def main():
    parsed = []
    per_date = {}
    raw_by_date = {}
    for compact in RESULT_DATES:
        date = datetime.strptime(compact, '%Y%m%d').date().isoformat()
        url = f'{BASE}/{compact}'
        raw = fetch(url)
        raw_by_date[compact] = raw
        rows = parse_results(raw, url, date)
        per_date[date] = len(rows)
        parsed.extend(rows)

    unique = {}
    for row in parsed:
        unique.setdefault(semantic_key(row), row)

    if len(unique) != EXPECTED_TIES:
        for compact, raw in raw_by_date.items():
            source_probe(raw, compact)
        raise SystemExit(
            f'ABORT: Extra Preliminary source coverage expected {EXPECTED_TIES} ties, got {len(unique)}; '
            f'per-date={per_date}'
        )

    draws = [row for row in unique.values() if row['home_score'] == row['away_score']]
    if len(draws) < 40:
        raise SystemExit(f'ABORT: expected at least 40 drawn Extra Preliminary ties, got {len(draws)}')

    amersham = [row for row in unique.values()
                if norm(row['home']) == norm('North Leigh') and norm(row['away']) == norm('Amersham Town')]
    if len(amersham) != 1 or amersham[0]['home_score'] != 2 or amersham[0]['away_score'] != 2:
        raise SystemExit(f'ABORT: Amersham regression source row missing or unexpected: {amersham}')

    data = json.loads(DATA_PATH.read_text(encoding='utf-8'))
    before = unique_round_rows(data, 'Extra Preliminary Round')
    changed = False
    for row in sorted(unique.values(), key=round_order):
        changed = add_result(data, row) or changed
    after = unique_round_rows(data, 'Extra Preliminary Round')

    if len(after) != EXPECTED_TIES:
        raise SystemExit(f'ABORT: canonical Extra Preliminary chronology expected {EXPECTED_TIES} ties, got {len(after)}')

    restored = len(after) - len(before)
    if changed:
        now = datetime.now(timezone.utc).isoformat()
        data['updated_at'] = now
        data['extra_preliminary_sync'] = {
            'source': 'Football Web Pages date pages',
            'source_urls': [f'{BASE}/{d}' for d in RESULT_DATES],
            'synced_at': now,
            'original_ties': len(after),
            'drawn_first_legs': len(draws),
            'new_original_results_restored': restored,
        }
        DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    print('EXTRA PRELIMINARY CHRONOLOGY: PASS')
    print('Source ties:', len(unique))
    print('Drawn first legs:', len(draws))
    print('Canonical ties before:', len(before))
    print('Canonical ties after:', len(after))
    print('Original results restored:', restored)
    print('Amersham anchor: North Leigh 2-2 Amersham Town: PASS')
    print('Competition state changed:', 'YES' if changed else 'NO (idempotent)')


if __name__ == '__main__':
    main()
