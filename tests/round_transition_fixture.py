"""Frozen real import plus explicitly synthetic replay/future-round scenarios.

Only temporary files are written. Rebuilt FA-shaped HTML is not a source capture.
"""
import copy
import gzip
import hashlib
import html
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/draw-transition-20261019'
sys.path.insert(0, str(ROOT / 'updater'))
import auto_draw as draw
import auto_round_results as results
import scheduled_archived_replays as archived

STATES = ('qualifying', 'proper-conditional', 'proper-resolved', 'proper-resolved-away',
          'second-proper', 'third-proper')


def frozen(name):
    manifest = json.loads((FIXTURE / 'manifest.json').read_text())
    raw = (FIXTURE / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == manifest['files'][name]['sha256'], name
    content = gzip.decompress(raw) if name.endswith('.gz') else raw
    assert hashlib.sha256(content).hexdigest() == manifest['files'][name]['uncompressed_sha256'], name
    return json.loads(content)


def fa_html(rows):
    """Reconstruct parser input from records; retain dates and round headings."""
    output = []
    for row in rows:
        date = datetime.strptime(row['date'], '%Y-%m-%d').strftime('%A %d %B %Y')
        output.append('<h2>' + html.escape(row['round']) + '</h2><h3>' + date + '</h3>')
        output.append('<table><tr>' + ''.join('<td>' + html.escape(str(value)) + '</td>' for value in
                      (row.get('kickoff', ''), row['home'], 'VS', row['away'])) + '</tr></table>')
    return ''.join(output)


def import_draw(data, rows):
    """Run the actual parser and publishing entrypoint with local-only sources."""
    pages = [fa_html(rows[:len(rows)//2]), fa_html(rows[len(rows)//2:])]
    def fetch(url):
        page = int(url.rsplit('=', 1)[1])
        return pages[page - 1] if page <= len(pages) else ''
    with tempfile.TemporaryDirectory(prefix='tffc-draw-input-') as tmp:
        path, report = Path(tmp) / 'competition.json', Path(tmp) / 'report.json'
        path.write_text(json.dumps(data))
        before = path.read_bytes()
        with patch.object(draw, 'DATA', path), patch.object(draw, 'REPORT', report), \
                patch.object(draw, 'fetch', side_effect=fetch), \
                patch('sys.argv', ['auto_draw.py', '--publish']):
            try:
                draw.main()
            except BaseException:
                assert path.read_bytes() == before, 'Rejected draw mutated canonical input'
                raise
        return json.loads(path.read_text()), json.loads(report.read_text())


def replay_source(data, home_wins=True):
    """Synthetic 2-0/0-2 results using real pending replay names/schedule."""
    rows = []
    for replay in draw.fixture_values(data['replays']):
        if replay['round'] != 'Fourth Round Qualifying Replay':
            continue
        date = datetime.strptime(replay['date'], '%Y-%m-%d').strftime('%A %d %B %Y')
        scores = '</td><td>2</td><td>0</td><td>' if home_wins else '</td><td>0</td><td>2</td><td>'
        rows.append('<h3>' + date + '</h3><table><tr><td>FT</td><td>' + html.escape(replay['home']) +
                    scores + html.escape(replay['away']) + '</td></tr></table>')
    return '<h1>Fixtures/Results, Fourth Qualifying Round Replay, 2026-2027</h1>' + ''.join(rows)


def resolve_replays(data, home_wins=True):
    before = copy.deepcopy(data)
    source = replay_source(data, home_wins)
    url = archived.audit.archived_replay_source('Fourth Round Qualifying')
    def fetch(requested):
        assert requested == url, requested
        return source
    candidate, report, _ = archived.collect(data, fetch, as_of=datetime(2026, 10, 24, tzinfo=timezone.utc))
    assert data == before, 'Replay collection mutated its input'
    assert report['status'] == 'staged', report
    assert report['staged']['staged_count'] == 11, report
    assert not any(draw.is_conditional_fixture(f) for f in draw.fixture_values(candidate['fixtures']))
    repeated, again, _ = archived.collect(candidate, fetch, as_of=datetime(2026, 10, 24, tzinfo=timezone.utc))
    assert repeated == candidate and again['status'] == 'no-outstanding-replays'
    return candidate


def future_round(data, target, date):
    """Synthetic decisive results and later draw; never claims future evidence."""
    data = copy.deepcopy(data)
    winners = []
    for fixture in draw.fixture_values(data['fixtures']):
        assert not draw.is_conditional_fixture(fixture)
        result = dict(fixture, home_score=2, away_score=0, winner=fixture['home'], status='FT',
                      decision='', source_url='https://example.test/synthetic-results')
        results.merge_result(data, result)
        winners.append(fixture['home'])
    count = draw.EXPECTED_ROUND_TIES[target]
    # Third Proper introduces new clubs; synthetic entrants are unmistakable.
    winners += [f'Synthetic New Entrant {i:02d}' for i in range(2 * count - len(winners))]
    assert len(winners) == 2 * count
    rows = [dict(round=target, home=winners[2*i], away=winners[2*i+1], date=date, kickoff='15:00')
            for i in range(count)]
    candidate, report = import_draw(data, rows)
    assert report['published'] and candidate['source_round'] == target
    # The FA draw parser supplies no venue. Model the later venue-enrichment
    # stage explicitly so future synthetic played ties have located venues.
    # This is test metadata, never asserted to be a club's real home ground.
    enriched = draw.fixture_values(candidate['fixtures'])
    for fixture in enriched:
        fixture['venue'] = dict(ground='Synthetic Rehearsal Ground', postcode='HP7 0EJ',
                               lat=51.676, lon=-0.607, verification='verified',
                               source='https://example.test/synthetic-venue')
    candidate['fixtures'] = draw.fixture_map(enriched)
    return candidate


def states(through):
    assert through in STATES, through
    before = frozen('competition-before.json.gz')
    published = frozen('competition-published.json.gz')
    observed = frozen('draw-watch-report.json')
    assert before['source_round'] == 'Fourth Round Qualifying'
    assert observed['target_ties_detected'] == 40 and observed['archived_outgoing_ties'] == 32
    output = {'qualifying': before}
    if through == 'qualifying':
        return output
    # The report records 11 old-round rows. Their original HTML was not saved:
    # model that shrinking catalogue using the canonical pending replay schedule.
    old = [dict(r, round='Fourth Round Qualifying') for r in draw.fixture_values(before['replays'])
           if r['round'] == 'Fourth Round Qualifying Replay']
    assert len(old) == observed['active_round_official_ties'] == 11
    promoted, report = import_draw(before, old + draw.fixture_values(published['fixtures']))
    expected = copy.deepcopy(published)
    expected.pop('updated_at')
    actual = copy.deepcopy(promoted)
    actual.pop('updated_at')
    assert actual == expected, 'Reconstructed import differs from the real published payload'
    assert report['replay_phase_verified'] == observed['replay_phase_verified']
    # Repeating the same official catalogue must not alter canonical state.
    repeated, _ = import_draw(promoted, old + draw.fixture_values(published['fixtures']))
    assert repeated == promoted
    output['proper-conditional'] = promoted
    if through == 'proper-conditional':
        return output
    if through == 'proper-resolved-away':
        output['proper-resolved-away'] = resolve_replays(promoted, home_wins=False)
        return output
    resolved = resolve_replays(promoted)
    output['proper-resolved'] = resolved
    if through == 'proper-resolved':
        return output
    second = future_round(resolved, 'Second Round Proper', '2026-12-05')
    output['second-proper'] = second
    if through == 'second-proper':
        return output
    third = future_round(second, 'Third Round Proper', '2027-01-09')
    output['third-proper'] = third
    return output
