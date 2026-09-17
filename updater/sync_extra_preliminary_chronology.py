#!/usr/bin/env python3
"""Restore the complete 2026-27 FA Cup Extra Preliminary Round chronology.

The FA draw contained 219 ties. Football Web Pages date pages for 7-9 August
supply 217 completed original ties when restricted to the actual
"Extra Preliminary Round" section. Aylesbury United v Flackwell Heath was
abandoned on 7 August and the rearranged original tie was completed on
12 August; Football Web Pages labels that completion as a replay, so the
verified Aylesbury record is used to classify it correctly. Marske United
were awarded their tie after Boro Rangers withdrew.

The write remains fail-closed: canonical chronology must finish with all
219 distinct original ties, and only exact, explicitly recognised parser or
classification artefacts may be removed.
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
EXPECTED_DATE_PAGE_PLAYED_TIES = 217
EXPECTED_PLAYED_TIES = 218
MAX_ARCHIVE_SHRINK = 3
UA = 'TinFoilFACupExtraPreliminaryChronology/1.0 (+https://anvilspringstien.github.io/tinfoilfacup/)'
PROBE_ANCHORS = {'20260807': 'Ascot United', '20260808': 'North Leigh', '20260809': 'Beverley Town'}

# Exact identity aliases observed between the existing canonical chronology and
# Football Web Pages. These are matching aliases only: stored/display names are
# not rewritten. Keep this list deliberately narrow and source-verified.
TEAM_IDENTITY_ALIASES = {
    'bedfont sports club': 'bedfont sports',
    'bournemouth poppies': 'bournemouth',
    'atherton lr': 'atherton laburnum rovers',
    'irlam': 'irlam town',
    'eastwood community': 'eastwood',
    'millbrook hampshire': 'millbrook',
    'royal wootton bassett town': 'royal wootton bassett',
    'sherbourne town': 'sherborne town',
    'st helens town': 'fc st helens',
    'sutton united birmingham': 'sutton united west midlands',
    'varndeanians': 'varndenians',
}

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

REARRANGED_ORIGINAL = {
    'round': 'Extra Preliminary Round',
    'date': '2026-08-12',
    'home': 'Aylesbury United',
    'away': 'Flackwell Heath',
    'home_score': 2,
    'away_score': 3,
    'winner': 'Flackwell Heath',
    'status': 'FT',
    'decision': '',
    'source_url': 'https://www.aylesburyunitedarchive.com/match/2026-08-12/aylesbury-united/vs/flackwell-heath',
    'note': 'Rearranged original tie after the 7 August fixture was abandoned following a power outage.',
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.buf = []
        self.events = []
        self.row = []
        self.cell = None
        self.cell_export = None

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
        if tag in ('h2', 'h3', 'h4'):
            self.buf = []
        if tag == 'tr':
            self.row = []
        if tag in ('td', 'th'):
            self.cell = []
            # Football Web Pages embeds hidden half-time scores inside team
            # cells. data-export contains the canonical cell value.
            self.cell_export = dict(attrs).get('data-export')

    def handle_data(self, data):
        if self.stack and self.stack[-1] in ('h2', 'h3', 'h4'):
            self.buf.append(data)
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            raw = self.cell_export if self.cell_export is not None else ''.join(self.cell)
            txt = ' '.join(str(raw).split())
            self.row.append(unescape(txt))
            self.cell = None
            self.cell_export = None
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
    s = re.sub(r'[^a-z0-9]+', ' ', s).strip()
    return TEAM_IDENTITY_ALIASES.get(s, s)


def aliases(name):
    suffix = re.compile(r'\s+(FC|AFC|CFC)$', re.I)
    out = {name, suffix.sub('', name)}
    if not suffix.search(name):
        out |= {name + ' FC', name + ' AFC'}
    return {x for x in out if x}


def strip_hidden_half_time(name):
    return re.sub(r'\(\d+\)$', '', str(name or '')).strip()


def score_int(value):
    value = str(value or '').strip()
    return int(value) if re.fullmatch(r'\d+', value) else None


def heading_key(value):
    return re.sub(r'\s+', ' ', str(value or '').strip().lower())


def parse_results(raw, url, date):
    parser = PageParser()
    parser.feed(raw)
    out = []
    in_original_section = False

    for kind, value in parser.events:
        if kind == 'heading':
            # Page headings (normally the date) are not round boundaries.
            # FWP marks each competition round inside the table itself.
            continue
        if kind != 'row':
            continue

        cells = [c.strip() for c in value if c.strip()]
        if len(cells) == 1:
            # Round boundaries are rendered as one-cell table-title rows such
            # as <th colspan="6">Extra Preliminary Round</th>. Every title row
            # resets state, preventing replay/other-round FT rows from leaking
            # into the original chronology.
            in_original_section = heading_key(cells[0]) == 'extra preliminary round'
            continue
        if not in_original_section:
            continue

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


def pair_key(row):
    return frozenset((norm(row.get('home')), norm(row.get('away'))))


def cleaned_semantic_key(row):
    cleaned = dict(row)
    cleaned['home'] = strip_hidden_half_time(row.get('home'))
    cleaned['away'] = strip_hidden_half_time(row.get('away'))
    return semantic_key(cleaned)


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


def purge_exact_round_rows(data, round_name, bad_keys):
    if not bad_keys:
        return False
    changed = False
    history = data.get('result_history') or {}
    for club, arr in history.items():
        if not isinstance(arr, list):
            continue
        kept = [
            row for row in arr
            if not (
                isinstance(row, dict)
                and row.get('round') == round_name
                and semantic_key(row) in bad_keys
            )
        ]
        if len(kept) != len(arr):
            history[club] = kept
            changed = True
    results = data.get('results') or {}
    for club, row in list(results.items()):
        if isinstance(row, dict) and row.get('round') == round_name and semantic_key(row) in bad_keys:
            del results[club]
            changed = True
    return changed


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

    date_page_played = {}
    for row in parsed:
        date_page_played.setdefault(semantic_key(row), row)

    # Hidden half-time annotations must never leak into newly parsed team names.
    polluted = [
        f"{row.get('home')} v {row.get('away')}"
        for row in date_page_played.values()
        if re.search(r'\(\d+\)$', str(row.get('home') or ''))
        or re.search(r'\(\d+\)$', str(row.get('away') or ''))
    ]
    if polluted:
        raise SystemExit(f'ABORT: hidden half-time score leaked into parsed team name(s): {polluted[:5]}')

    source_complete = len(date_page_played) == EXPECTED_DATE_PAGE_PLAYED_TIES
    if len(date_page_played) > EXPECTED_DATE_PAGE_PLAYED_TIES:
        raise SystemExit(
            f'ABORT: Extra Preliminary original-section source has {len(date_page_played)} ties; '
            f'expected at most {EXPECTED_DATE_PAGE_PLAYED_TIES}; per-date={per_date}'
        )
    if not source_complete:
        for compact, raw in raw_by_date.items():
            source_probe(raw, compact)
        missing_count = EXPECTED_DATE_PAGE_PLAYED_TIES - len(date_page_played)
        source_keys = set(date_page_played)
        rearranged_key = semantic_key(REARRANGED_ORIGINAL)
        walkover_key = semantic_key(WALKOVER)
        canonical_date_page_keys = {
            key for key, row in before.items()
            if key not in {rearranged_key, walkover_key}
            and not (
                row.get('decision') == 'walkover'
                or (row.get('home_score') is None and row.get('away_score') is None)
            )
        }
        safe_archive_shrink = (
            0 < missing_count <= MAX_ARCHIVE_SHRINK
            and len(before) == EXPECTED_TIES
            and source_keys.issubset(canonical_date_page_keys)
        )
        if not safe_archive_shrink:
            raise SystemExit(
                f'ABORT: Extra Preliminary dated-page original-section coverage expected '
                f'{EXPECTED_DATE_PAGE_PLAYED_TIES} ties, got {len(date_page_played)}; '
                f'per-date={per_date}; canonical={len(before)}'
            )
        missing = sorted(canonical_date_page_keys - source_keys)
        print('EXTRA PRELIMINARY PLAYED-RESULT ARCHIVE SHRINK DETECTED')
        print(
            f'Live historical source exposes {len(date_page_played)}/'
            f'{EXPECTED_DATE_PAGE_PLAYED_TIES} previously verified dated-page original ties.'
        )
        print('Canonical chronology remains complete and every live source row is an exact semantic subset: PASS')
        for key in missing:
            print('Source no longer exposes:', describe_key(key))
        for key in missing:
            date_page_played[key] = before[key]
        print('Verified canonical chronology retained for the missing historical source row(s).')

    played = dict(date_page_played)
    rearranged_key = semantic_key(REARRANGED_ORIGINAL)
    played.setdefault(rearranged_key, REARRANGED_ORIGINAL)
    if len(played) != EXPECTED_PLAYED_TIES:
        raise SystemExit(
            f'ABORT: dated-page originals + verified rearranged original expected '
            f'{EXPECTED_PLAYED_TIES} played ties, got {len(played)}'
        )

    all_ties = dict(played)
    all_ties.setdefault(semantic_key(WALKOVER), WALKOVER)
    if len(all_ties) != EXPECTED_TIES:
        raise SystemExit(f'ABORT: played results + verified walkover expected {EXPECTED_TIES} ties, got {len(all_ties)}')

    distinct_pairs = {}
    for row in all_ties.values():
        distinct_pairs.setdefault(pair_key(row), []).append(row)
    if len(distinct_pairs) != EXPECTED_TIES:
        duplicates = [
            ' | '.join(describe_key(semantic_key(row)) for row in rows)
            for rows in distinct_pairs.values() if len(rows) > 1
        ]
        raise SystemExit(
            f'ABORT: verified Extra Preliminary originals cover {len(distinct_pairs)} distinct pairs; '
            f'expected {EXPECTED_TIES}; duplicates={duplicates[:5]}'
        )

    draws = [row for row in played.values() if row['home_score'] == row['away_score']]
    if len(draws) < 40:
        raise SystemExit(f'ABORT: expected at least 40 drawn Extra Preliminary ties, got {len(draws)}')

    amersham_source = [row for row in played.values()
                       if norm(row['home']) == norm('North Leigh') and norm(row['away']) == norm('Amersham Town')]
    amersham_canonical = [row for row in before.values()
                          if norm(row['home']) == norm('North Leigh') and norm(row['away']) == norm('Amersham Town')]
    amersham = amersham_source or amersham_canonical
    if len(amersham) != 1 or amersham[0]['home_score'] != 2 or amersham[0]['away_score'] != 2:
        raise SystemExit(f'ABORT: Amersham regression row missing or unexpected: source={amersham_source} canonical={amersham_canonical}')

    # Aylesbury-Flackwell is a rearranged original tie, not a replay. Remove
    # only the exact misclassified 12 August 2-3 replay copy.
    replay_rows = unique_round_rows(data, 'Extra Preliminary Round Replay')
    rearranged_replay_keys = {
        key for key in replay_rows
        if key == rearranged_key
    }
    replay_reclassified = bool(rearranged_replay_keys)
    changed = purge_exact_round_rows(
        data, 'Extra Preliminary Round Replay', rearranged_replay_keys
    )

    # Repair only old original rows that become an exact live-source match
    # after removing a trailing hidden half-time score. Any other unmatched old
    # row is a hard failure so historical differences cannot be silently
    # normalised away.
    source_keys = set(all_ties)
    parser_artifact_keys = set()
    unexpected_old = []
    for key, row in before.items():
        if key in source_keys:
            continue
        cleaned_key = cleaned_semantic_key(row)
        had_hidden_half_time = (
            strip_hidden_half_time(row.get('home')) != str(row.get('home') or '').strip()
            or strip_hidden_half_time(row.get('away')) != str(row.get('away') or '').strip()
        )
        if had_hidden_half_time and cleaned_key in source_keys:
            parser_artifact_keys.add(key)
        else:
            unexpected_old.append(key)

    if unexpected_old:
        print('UNEXPECTED PRE-EXISTING EXTRA PRELIMINARY ROWS:')
        for key in sorted(unexpected_old):
            print('  ', describe_key(key))
        raise SystemExit(
            f'ABORT: {len(unexpected_old)} pre-existing Extra Preliminary row(s) do not match the verified 219-tie chronology '
            'and are not exact hidden-half-time parser artefacts.'
        )

    changed = purge_exact_round_rows(
        data, 'Extra Preliminary Round', parser_artifact_keys
    ) or changed
    for row in sorted(all_ties.values(), key=round_order):
        changed = add_result(data, row) or changed
    after = unique_round_rows(data, 'Extra Preliminary Round')

    if len(after) != EXPECTED_TIES:
        raise SystemExit(f'ABORT: canonical Extra Preliminary chronology expected {EXPECTED_TIES} ties, got {len(after)}')
    after_pairs = {pair_key(row) for row in after.values()}
    if len(after_pairs) != EXPECTED_TIES:
        raise SystemExit(
            f'ABORT: canonical Extra Preliminary chronology has {len(after_pairs)} distinct pairs; '
            f'expected {EXPECTED_TIES}'
        )

    walkovers = [row for row in after.values() if row.get('decision') == 'walkover']
    if len(walkovers) != 1 or norm(walkovers[0].get('home')) != norm('Marske United') or norm(walkovers[0].get('winner')) != norm('Marske United'):
        raise SystemExit(f'ABORT: verified Marske United walkover missing or duplicated: {walkovers}')

    aylesbury_original = [
        row for row in after.values()
        if semantic_key(row) == rearranged_key
    ]
    aylesbury_replay = [
        row for row in unique_round_rows(data, 'Extra Preliminary Round Replay').values()
        if pair_key(row) == pair_key(REARRANGED_ORIGINAL)
    ]
    if len(aylesbury_original) != 1 or aylesbury_replay:
        raise SystemExit(
            f'ABORT: Aylesbury-Flackwell rearranged-original classification failed: '
            f'original={aylesbury_original} replay={aylesbury_replay}'
        )

    restored = len(after) - len(before)
    if changed:
        now = datetime.now(timezone.utc).isoformat()
        data['updated_at'] = now
        data['extra_preliminary_sync'] = {
            'source': 'Football Web Pages dated original-round sections + verified Aylesbury rearrangement + verified Marske United walkover',
            'source_urls': (
                [f'{BASE}/{d}' for d in RESULT_DATES]
                + [REARRANGED_ORIGINAL['source_url'], WALKOVER['source_url']]
            ),
            'synced_at': now,
            'dated_page_original_ties_visible': len(date_page_played),
            'dated_page_source_complete': source_complete,
            'verified_rearranged_originals': 1,
            'played_original_ties': len(played),
            'walkovers': 1,
            'original_ties': len(after),
            'drawn_first_legs_visible': len(draws),
            'misclassified_replay_rows_reclassified': 1 if replay_reclassified else 0,
            'parser_artifacts_repaired': len(parser_artifact_keys),
            'net_original_ties_restored': restored,
        }
        DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    print('EXTRA PRELIMINARY CHRONOLOGY: PASS')
    print('Dated-page original-section ties visible:', len(date_page_played))
    print('Verified rearranged originals:', 1)
    print('Verified played originals total:', len(played))
    print('Verified walkovers:', 1)
    print('Canonical ties before:', len(before))
    print('Misclassified Aylesbury replay reclassified:', 'YES' if replay_reclassified else 'NO (already clean)')
    print('Parser artefact rows repaired:', len(parser_artifact_keys))
    print('Canonical ties after:', len(after))
    print('Distinct original pairs after:', len(after_pairs))
    print('Net original ties restored:', restored)
    print('Marske United v Boro Rangers walkover: PASS')
    print('Aylesbury United 2-3 Flackwell Heath rearranged original: PASS')
    print('Amersham anchor: North Leigh 2-2 Amersham Town: PASS')
    print('Competition state changed:', 'YES' if changed else 'NO (idempotent)')


if __name__ == '__main__':
    main()
