"""Saturday originals -> Monday draw -> Tuesday replay, through real entrypoints."""
import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'updater'))
import auto_draw as draw
import auto_round_results as scan
import scheduled_archived_replays as archived


def state(round_name='Fourth Round Qualifying'):
    first = dict(round=round_name, home='Alpha Town', away='Beta City', date='2026-10-17', kickoff='15:00',
                 venue={'ground': 'Original Ground', 'postcode': 'AA1 1AA', 'source': 'https://example.test/ground'})
    second = dict(round=round_name, home='Gamma Town', away='Delta City', date='2026-10-17')
    replay = dict(round=round_name + ' Replay', home='Beta City', away='Alpha Town', date='2026-10-20', kickoff='19:45',
                  source_url='https://example.test/fixtures', venue={'ground': 'Replay Ground', 'postcode': 'BB1 1BB', 'source': 'https://example.test/ground'})
    data = dict(source_round=round_name, source_tie_count=2, fixtures=draw.fixture_map([first, second]),
                replays=draw.fixture_map([replay]), results={}, result_history={})
    scan.merge_result(data, dict(first, home_score=1, away_score=1, winner='', decision='draw-replay', status='FT', source_url='https://example.test/results'))
    scan.merge_result(data, dict(second, home_score=2, away_score=0, winner='Gamma Town', decision='', status='FT', source_url='https://example.test/results'))
    return data


def next_draw(round_name):
    target = draw.ROUND_ORDER[draw.ROUND_ORDER.index(round_name) + 1]
    count = draw.EXPECTED_ROUND_TIES.get(target, 20)
    fixtures = [dict(round=target, home='Alpha Town or Beta City', away='Next United', date='2026-11-07', kickoff='15:00',
                     venue={'ground': 'Next Ground', 'postcode': 'CC1 1CC', 'source': 'https://example.test/ground'})]
    fixtures += [dict(round=target, home=f'Home Club {i}', away=f'Away Club {i}', date='2026-11-07') for i in range(1, count)]
    return target, fixtures


def replay_html(round_name, score='2', other='1', note=''):
    return (f'<h1>Fixtures/Results, {scan.fwp_round_label(round_name)} Replay, 2026-2027</h1>'
            f'<h3>Tuesday 20 October 2026</h3><table><tr><td>FT</td><td>Beta City</td>'
            f'<td>{score}</td><td>{other}</td><td>Alpha Town</td></tr><tr><td>{note}</td></tr></table>')


class LifecycleTests(unittest.TestCase):
    def promote(self, data, target_rows=None):
        target, rows = next_draw(data['source_round'])
        rows = target_rows if target_rows is not None else rows
        with tempfile.TemporaryDirectory() as tmp:
            dp, rp = Path(tmp)/'competition.json', Path(tmp)/'report.json'
            dp.write_text(json.dumps(data))
            with patch.object(draw, 'DATA', dp), patch.object(draw, 'REPORT', rp), patch.object(draw, 'fetch', return_value='html'), patch.object(draw, 'parse_page', return_value=rows), patch('sys.argv', ['auto_draw.py', '--publish', '--max-pages', '1']):
                try:
                    draw.main()
                except SystemExit:
                    self.assertEqual(json.loads(dp.read_text()), data)
                    raise
            return json.loads(dp.read_text()), target

    def run_results(self, data, replay_source, live_source=''):
        active = data['source_round']
        previous = draw.ROUND_ORDER[draw.ROUND_ORDER.index(active)-1]
        urls = {scan.fwp_round_url(active): f'<h1>Fixtures/Results, {scan.fwp_round_label(active)}, 2026-2027</h1>',
                scan.fwp_round_url(previous) + '-replay': replay_source,
                scan.FWP_LIVE_URL: live_source, 'https://www.thefa.com/competitions/thefacup/results': ''}
        requested = []
        def fetch(url):
            requested.append(url)
            return urls[url]
        with tempfile.TemporaryDirectory() as tmp:
            dp, rp, cp = (Path(tmp)/name for name in ('competition.json', 'report.json', 'capture.json'))
            dp.write_text(json.dumps(data))
            with patch.object(scan, 'DATA', dp), patch.object(scan, 'REPORT', rp), patch.object(scan, 'SOURCE_CAPTURE', cp), patch.object(scan, 'fetch', side_effect=fetch), patch('sys.argv', ['auto_round_results.py', '--publish']):
                try:
                    scan.main()
                except SystemExit:
                    self.assertEqual(json.loads(dp.read_text()), data)
                    self.assertIn("archived_replays", json.loads(cp.read_text()))
                    raise
            return json.loads(dp.read_text()), json.loads(rp.read_text()), requested

    def test_complete_sequence_every_replay_eligible_round(self):
        for round_name in archived.audit.ROUNDS[:-1]:
            with self.subTest(round=round_name):
                saturday = state(round_name)
                original_history = copy.deepcopy(saturday['result_history'])
                replay = draw.fixture_values(saturday['replays'])[0]
                self.assertTrue(draw.verified_replay_phase(saturday, [dict(replay, round=round_name)], 2))
                monday, target = self.promote(saturday)
                self.assertEqual(monday['source_round'], target)
                self.assertEqual(monday['result_history'], original_history)
                self.assertEqual(monday['replays'], saturday['replays'])
                self.assertEqual(len(monday['round_fixtures'][round_name]), 2)
                tuesday, report, requested = self.run_results(monday, replay_html(round_name))
                self.assertIn(scan.fwp_round_url(round_name) + '-replay', requested)
                self.assertEqual(report['archived_replays']['status'], 'staged')
                played = [r for r in scan.history_rows(tuesday) if r['round'] == round_name + ' Replay']
                self.assertEqual(len(played), 1)
                self.assertEqual(played[0]['winner'], 'Beta City')
                self.assertEqual(played[0]['kickoff'], '19:45')
                self.assertEqual(played[0]['venue']['postcode'], 'BB1 1BB')
                next_fixture = tuesday['fixtures']['Beta City']
                self.assertEqual(next_fixture['home'], 'Beta City')
                self.assertNotIn('Alpha Town', tuesday['fixtures'])
                self.assertEqual(next_fixture['date'], '2026-11-07')
                self.assertEqual(next_fixture['venue']['postcode'], 'CC1 1CC')
                self.assertEqual(tuesday['round_fixtures'], monday['round_fixtures'])
                for club, history in original_history.items():
                    for result in history:
                        self.assertIn(result, tuesday['result_history'][club])
                repeated, again, requests = self.run_results(tuesday, replay_html(round_name))
                self.assertEqual(repeated, tuesday)
                self.assertNotIn(scan.fwp_round_url(round_name) + '-replay', requests)

    def test_thirty_two_originals_eleven_replays_after_first_proper_draw(self):
        rnd = 'Fourth Round Qualifying'
        saturday = dict(source_round=rnd, source_tie_count=32, fixtures={}, replays={}, results={}, result_history={})
        next_rows = []
        source_rows = []
        for i in range(32):
            home, away = f'Original Home {i:03d}', f'Original Away {i:03d}'
            original = dict(round=rnd, home=home, away=away, date='2026-10-17')
            saturday['fixtures'].update(draw.fixture_map([original]))
            drawn = i < 11
            scan.merge_result(saturday, dict(original, home_score=1 if drawn else 2, away_score=1 if drawn else 0,
                                            winner='' if drawn else home, status='FT', decision='draw-replay' if drawn else '',
                                            source_url='https://example.test/results'))
            if drawn:
                replay = dict(round=rnd + ' Replay', home=away, away=home, date='2026-10-20',
                              source_url='https://example.test/fixtures')
                saturday['replays'].update(draw.fixture_map([replay]))
                next_rows.append(dict(round='First Round Proper', home=home + ' or ' + away,
                                      away=f'League Club {i}', date='2026-11-07'))
                source_rows.append(f'<tr><td>FT</td><td>{away}</td><td>2</td><td>0</td><td>{home}</td></tr>')
        next_rows += [dict(round='First Round Proper', home=f'Next Home {i}', away=f'Next Away {i}', date='2026-11-07')
                      for i in range(11,40)]
        monday, _ = self.promote(saturday, next_rows)
        source = '<h1>Fixtures/Results, Fourth Qualifying Round Replay, 2026-2027</h1><h3>Tuesday 20 October 2026</h3><table>' + ''.join(source_rows) + '</table>'
        tuesday, report, _ = self.run_results(monday, source)
        self.assertEqual(report['archived_replays']['staged']['staged_count'], 11)
        self.assertEqual(len(report['archived_replays']['resolutions']), 11)
        self.assertEqual(len(draw.fixture_values(tuesday['fixtures'])), 40)
        self.assertEqual(len(tuesday['round_fixtures'][rnd]), 32)
        self.assertEqual(len(scan.history_rows(tuesday)), 43)
        for i in range(11):
            self.assertEqual(tuesday['fixtures'][f'Original Away {i:03d}']['home'], f'Original Away {i:03d}')

        # The overnight failure: the archive has a level FT score, while the
        # live page adds the penalty winner. The shared policy now accepts that explicit decision;
        # all eleven replays must advance without club-specific evidence wiring.
        mixed = source.replace('<td>2</td><td>0</td><td>Original Home 000</td>',
                               '<td>2</td><td>2</td><td>Original Home 000</td>')
        live = ('<h3>Tuesday 20 October 2026</h3><table><tr><td>FT</td>'
                '<td>Original Away 000</td><td>2</td><td>2</td><td>Original Home 000</td></tr>'
                '<tr><td>Original Away 000 win on penalties</td></tr></table>')
        partial, report, _ = self.run_results(monday, mixed, live)
        self.assertEqual(report['archived_replays']['status'], 'staged')
        self.assertEqual(report['archived_replays']['staged']['staged_count'], 11)
        self.assertEqual(len(report['archived_replays']['held']), 0)
        self.assertEqual(len(report['archived_replays']['audit']['penalty_refinements']), 1)
        self.assertEqual(len(draw.fixture_values(partial['fixtures'])), 40)
        self.assertEqual(partial['round_fixtures'], monday['round_fixtures'])
        self.assertEqual(partial['fixtures']['Original Away 000']['home'], 'Original Away 000')
        for i in range(1, 11):
            self.assertEqual(partial['fixtures'][f'Original Away {i:03d}']['home'], f'Original Away {i:03d}')
        repeated, again, _ = self.run_results(partial, mixed, live)
        self.assertEqual(repeated, partial)
        self.assertEqual(again['archived_replays']['status'], 'no-outstanding-replays')

        absent = source.replace(source_rows[0], '')
        partial, report, _ = self.run_results(monday, absent)
        self.assertEqual(report['archived_replays']['staged']['staged_count'], 10)
        self.assertEqual(len(partial['pending_match_decisions']), 1)
        recovered, _, _ = self.run_results(partial, source)
        self.assertFalse(recovered['pending_match_decisions'])
        self.assertEqual(recovered['fixtures']['Original Away 000']['home'], 'Original Away 000')

    def test_first_proper_rejects_39_and_41_ties_without_mutating_history(self):
        saturday = state('Fourth Round Qualifying')
        before = copy.deepcopy(saturday)
        _, forty = next_draw('Fourth Round Qualifying')
        too_many = forty + [dict(round='First Round Proper', home='Extra Home', away='Extra Away', date='2026-11-07')]
        for fixtures in (forty[:-1], too_many):
            with self.subTest(ties=len(fixtures)), self.assertRaisesRegex(SystemExit, 'expected 40 First Round Proper ties'):
                self.promote(saturday, fixtures)
            self.assertEqual(saturday, before)

    def test_awaiting_future_replays_is_noop(self):
        monday, _ = self.promote(state())
        before = copy.deepcopy(monday)
        source = '<h1>Fixtures/Results, Fourth Qualifying Round Replay, 2026-2027</h1>'
        candidate, report, _ = archived.collect(monday, lambda _: source, as_of=datetime(2026,10,19,tzinfo=timezone.utc))
        self.assertEqual(report['status'], 'awaiting-replays')
        self.assertEqual(candidate, before)
        self.assertEqual(monday, before)

    def test_missing_due_replay_is_held_and_wrong_round_source_fails_closed(self):
        monday, _ = self.promote(state())
        before = copy.deepcopy(monday)
        candidate,report,_ = archived.collect(monday, lambda _: '<h1>Fixtures/Results, Fourth Qualifying Round Replay, 2026-2027</h1>',
                                              as_of=datetime(2026,10,22,tzinfo=timezone.utc))
        self.assertEqual(report['status'], 'evidence-held')
        self.assertEqual(len(candidate['pending_match_decisions']),1)
        self.assertEqual(candidate['result_history'],monday['result_history'])
        with self.assertRaises((ValueError,SystemExit)):
            archived.collect(monday,lambda _: '<h1>Fixtures/Results, Third Qualifying Round Replay, 2026-2027</h1>')
        self.assertEqual(monday,before)

    def test_clear_penalties_from_accepted_source_advance(self):
        monday, _ = self.promote(state())
        before = copy.deepcopy(monday)
        candidate, report, _ = archived.collect(monday, lambda _: replay_html('Fourth Round Qualifying', '1', '1', 'Beta City win on penalties'),
                                                as_of=datetime(2026,10,22,tzinfo=timezone.utc))
        self.assertEqual(report['status'], 'staged')
        self.assertFalse(report['held'])
        self.assertEqual(candidate['fixtures']['Beta City']['home'], 'Beta City')
        self.assertEqual(monday, before)

    def test_reversed_orientation_without_draw_ancestry_cannot_publish(self):
        monday, _ = self.promote(state())
        for rows in monday['result_history'].values():
            for row in rows:
                if row.get('decision') == 'draw-replay':
                    row.update(home_score=2, away_score=1, winner='Alpha Town', decision='')
        before = copy.deepcopy(monday)
        with self.assertRaises(ValueError):
            archived.resolve_conditionals(monday, 'Fourth Round Qualifying')
        self.assertEqual(monday, before)

    def test_double_conditional_partial_results_and_independent_hold(self):
        saturday = state()
        for history in saturday['result_history'].values():
            for result in history:
                if result['home'] == 'Gamma Town':
                    result.update(home_score=0, away_score=0, winner='', decision='draw-replay')
        for result in saturday['results'].values():
            if result['home'] == 'Gamma Town':
                result.update(home_score=0, away_score=0, winner='', decision='draw-replay')
        second_replay = dict(round='Fourth Round Qualifying Replay', home='Delta City', away='Gamma Town',
                             date='2026-10-20', source_url='https://example.test/fixtures')
        saturday['replays'].update(draw.fixture_map([second_replay]))
        monday, _ = self.promote(saturday)
        fixtures = draw.fixture_values(monday['fixtures'])
        fixtures[0]['away'] = 'Gamma Town or Delta City'
        monday['fixtures'] = draw.fixture_map(fixtures)
        early = datetime(2026,10,20,22,tzinfo=timezone.utc)
        partial, report, _ = archived.collect(monday, lambda _: replay_html('Fourth Round Qualifying'), as_of=early)
        self.assertEqual(report['status'], 'staged')
        self.assertEqual(partial['fixtures']['Beta City']['away'], 'Gamma Town or Delta City')
        # A contradictory non-level penalty score stays held while the clear replay advances.
        penalty_row = '<tr><td>FT</td><td>Delta City</td><td>2</td><td>1</td><td>Gamma Town</td></tr><tr><td>Delta City win on penalties</td></tr>'
        mixed_source = replay_html('Fourth Round Qualifying').replace('</table>', penalty_row + '</table>')
        partial, report, _ = archived.collect(monday, lambda _: mixed_source, as_of=early)
        self.assertEqual(report['status'], 'partial-ready')
        self.assertEqual(len(report['held']), 1)
        self.assertEqual(partial['fixtures']['Beta City']['away'], 'Gamma Town or Delta City')
        final_source = mixed_source.replace('<td>2</td><td>1</td><td>Gamma Town</td>', '<td>3</td><td>1</td><td>Gamma Town</td>').replace('Delta City win on penalties', '')
        complete, report, _ = archived.collect(partial, lambda _: final_source, as_of=early)
        self.assertEqual(complete['fixtures']['Beta City']['away'], 'Delta City')
        self.assertNotIn('conditional', complete['fixtures']['Beta City'])

    def test_missing_archive_or_schedule_cannot_publish(self):
        monday, _ = self.promote(state())
        for key in ('round_fixtures', 'replays'):
            bad = copy.deepcopy(monday)
            bad[key] = {}
            before = copy.deepcopy(bad)
            with self.assertRaises(ValueError):
                archived.collect(bad, lambda _: replay_html('Fourth Round Qualifying'))
            self.assertEqual(bad, before)

    def test_source_failure_leaves_publish_input_unchanged(self):
        monday, _ = self.promote(state())
        with self.assertRaises(SystemExit):
            self.run_results(monday, '<h1>Fixtures/Results, Third Qualifying Round Replay, 2026-2027</h1>')

    def test_generic_abbreviations_preserve_archive_and_source_identity(self):
        saturday = state('Second Round Qualifying')
        # Substitute full sourced names and abbreviated FA archive names.
        raw = json.dumps(saturday).replace('Alpha Town', 'Example United').replace('Beta City', 'Other Town')
        saturday = json.loads(raw)
        original_fixtures = draw.fixture_values(saturday['fixtures'])
        original_fixtures[0]['home'] = 'Example Utd'
        saturday['fixtures'] = draw.fixture_map(original_fixtures)
        monday, _ = self.promote(saturday)
        fixtures = draw.fixture_values(monday['fixtures'])
        fixtures[0]['home'] = 'Example United or Other Town'
        monday['fixtures'] = draw.fixture_map(fixtures)
        source = replay_html('Second Round Qualifying').replace('Alpha Town', 'Example United').replace('Beta City', 'Other Town')
        before = copy.deepcopy(monday)
        candidate, report, _ = archived.collect(monday, lambda _: source)
        self.assertEqual(report['status'], 'staged')
        self.assertEqual(candidate['fixtures']['Other Town']['home'], 'Other Town')
        self.assertEqual(candidate['round_fixtures'], before['round_fixtures'])
        self.assertEqual(monday, before)

    def test_workflow_executes_lifecycle_guards_before_candidate_build(self):
        workflow = (Path(__file__).resolve().parents[1]/'.github/workflows/scan-results.yml').read_text()
        self.assertLess(workflow.index('test_round_replay_lifecycle.py\' -v'), workflow.index('- name: Scan active round'))
        self.assertIn('updater/scheduled_archived_replays.py', workflow)


if __name__ == '__main__':
    unittest.main()
