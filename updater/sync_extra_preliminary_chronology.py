#!/usr/bin/env python3
"""Restore the complete 2026-27 FA Cup Extra Preliminary Round chronology.

The round contained 219 drawn ties but only 218 played matches: Marske United
were awarded their tie after Boro Rangers withdrew. Football Web Pages date pages
supply the played scorelines; the verified walkover is added explicitly. The
write remains fail-closed: canonical chronology must finish with all 219 ties.
If the historical played-results source later drops a small number of already
verified rows, an exact canonical superset may be retained; contradictions or
substantial source loss still abort.
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
EXPECTED_PLAYED_TIES = 218
MAX_ARCHIVE_SHRINK = 3
UA = 'TinFoilFACupExtraPreliminaryChronology/1.0 (+https://anvilspringstien.github.io/tinfoilfacup/)'
PROBE_ANCHORS = {'20260807': 'Ascot United', '20260808': 'North Leigh', '20260809': 'Beverley Town'}
WALKOVER = {
    'round': 'Extra Preliminary Round',
    'date': '2026-08-08',
    'home': 'Marske United',
    'away': 'Boro Rangers',
    'home_score': None,
    'away_score': None,
    'winner': 'Marske United',
    'status': 'AWARDED',
    'decision': 'walkover',
    'source_url': 'https://www.marskeunitedfc.org/news/seasiders-given-emirates-fa-cup-extrapreliminary-round-bye-2991492.html',
    'note': 'Marske United awarded a walkover after Boro Rangers withdrew from the competition.',
}


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
        status_i = next((i for i, cell in enumerate(cells) if cell.upper().startswith('FT')), None)
        if status_i is None or len(cells) < status_i + 5:
            continue
        home = cells[status_i + 1]
        hs = score_int(cells[status_i + 2])
        away_score = score_int(cells[status_i + 3])
        away = cells[status_i + 4]
        if hs is None or away_score is None or not home or not away:
            continue
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
    print(f'SOURCE PROBE {compact}: bytes={len(raw)} tr={raw.lower().count("<tr")} td={raw.lower().count("<td")} anchor={anchor!r} index={idx}')
    print('SOURCE PROBE SNIPPET:', snippet)


def semantic_key(row):
    return (
        norm(row.get('home')),
        norm(row.get('away')),
        str(row.get('date') or ''),
        row.get('home_score'),
        row.get('away_score'),
    )


def describe_key(key):
    home, away, date, hs, ass = key
    score = 'AWARDED' if hs is None and ass is None else f'{hs}-{ass}'
    return f'{date}: {home} {score} {away}'


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
    data = json.loads(DATA_PATH.read_text(encoding='utf-8'))
    before = unique_round_rows(data, 'Extra Preliminary Round')

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

    played = {}
    for row in parsed:
        played.setdefault(semantic_key(row), row)

    source_complete = len(played) == EXPECTED_PLAYED_TIES
    if len(played) > EXPECTED_PLAYED_TIES:
        raise SystemExit(
            f'ABORT: Extra Preliminary played source has {len(played)} ties; expected at most {EXPECTED_PLAYED_TIES}; '
            f'per-date={per_date}'
        )
    if not source_complete:
        for compact, raw in raw_by_date.items():
            source_probe(raw, compact)
        missing_count = EXPECTED_PLAYED_TIES - len(played)
        source_keys = set(played)
        canonical_played_keys = {
            key for key, row in before.items()
            if not (row.get('decision') == 'walkover' or (row.get('home_score') is None and row.get('away_score') is None))
        }
        safe_archive_shrink = (
            0 < missing_count <= MAX_ARCHIVE_SHRINK
            and len(before) == EXPECTED_TIES
            and source_keys.issubset(canonical_played_keys)
        )
        if not safe_archive_shrink:
            raise SystemExit(
                f'ABORT: Extra Preliminary played-source coverage expected {EXPECTED_PLAYED_TIES} ties, got {len(played)}; '
                f'per-date={per_date}; canonical={len(before)}'
            )
        missing = sorted(canonical_played_keys - source_keys)
        print('EXTRA PRELIMINARY PLAYED-RESULT ARCHIVE SHRINK DETECTED')
        print(f'Live historical source exposes {len(played)}/{EXPECTED_PLAYED_TIES} previously verified played ties.')
        print('Canonical chronology remains complete and every live source row is an exact semantic subset: PASS')
        for key in missing:
            print('Source no longer exposes:', describe_key(key))
        print('Verified canonical chronology retained; no historical row removed.')

    all_ties = dict(played)
    all_ties.setdefault(semantic_key(WALKOVER), WALKOVER)
    if len(all_ties) != EXPECTED_TIES:
        raise SystemExit(f'ABORT: played results + verified walkover expected {EXPECTED_TIES} ties, got {len(all_ties)}')

    draws = [row for row in played.values() if row['home_score'] == row['away_score']]
    if len(draws) < 40:
        raise SystemExit(f'ABORT: expected at least 40 drawn Extra Preliminary ties in current played source, got {len(draws)}')

    amersham_source = [row for row in played.values()
                       if norm(row['home']) == norm('North Leigh') and norm(row['away']) == norm('Amersham Town')]
    amersham_canonical = [row for row in before.values()
                          if norm(row['home']) == norm('North Leigh') and norm(row['away']) == norm('Amersham Town')]
    amersham = amersham_source or amersham_canonical
    if len(amersham) != 1 or amersham[0]['home_score'] != 2 or amersham[0]['away_score'] != 2:
        raise SystemExit(f'ABORT: Amersham regression row missing or unexpected: source={amersham_source} canonical={amersham_canonical}')

    changed = False
    for row in sorted(all_ties.values(), key=round_order):
        changed = add_result(data, row) or changed
    after = unique_round_rows(data, 'Extra Preliminary Round')

    if len(after) != EXPECTED_TIES:
        raise SystemExit(f'ABORT: canonical Extra Preliminary chronology expected {EXPECTED_TIES} ties, got {len(after)}')
    walkovers = [row for row in after.values() if row.get('decision') == 'walkover']
    if len(walkovers) != 1 or norm(walkovers[0].get('home')) != norm('Marske United') or norm(walkovers[0].get('winner')) != norm('Marske United'):
        raise SystemExit(f'ABORT: verified Marske United walkover missing or duplicated: {walkovers}')

    restored = len(after) - len(before)
    if changed:
        now = datetime.now(timezone.utc).isoformat()
        data['updated_at'] = now
        data['extra_preliminary_sync'] = {
            'source': 'Football Web Pages date pages + verified Marske United walkover',
            'source_urls': [f'{BASE}/{d}' for d in RESULT_DATES] + [WALKOVER['source_url']],
            'synced_at': now,
            'played_source_ties_visible': len(played),
            'played_source_complete': source_complete,
            'walkovers': 1,
            'original_ties': len(after),
            'drawn_first_legs_visible': len(draws),
            'new_original_results_restored': restored,
        }
        DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    print('EXTRA PRELIMINARY CHRONOLOGY: PASS')
    print('Played source ties visible:', len(played))
    print('Verified walkovers:', 1)
    print('Canonical ties before:', len(before))
    print('Canonical ties after:', len(after))
    print('Original ties restored:', restored)
    print('Marske United v Boro Rangers walkover: PASS')
    print('Amersham anchor: North Leigh 2-2 Amersham Town: PASS')
    print('Competition state changed:', 'YES' if changed else 'NO (idempotent)')


if __name__ == '__main__':
    main()
