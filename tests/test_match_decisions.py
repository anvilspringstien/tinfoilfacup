"""One source policy and fixture boundary for every round and club."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'updater'))
import auto_draw as draw
import auto_round_results as scan
from match_decisions import classify_batch, publisher, retain_holds
from retry_match_decisions import retry_archived_holds

SOURCE = scan.fwp_round_url('First Round Proper')
LIVE = scan.FWP_LIVE_URL


def fixture(home='Home Town', away='Away City', rnd='First Round Proper'):
    return dict(home=home, away=away, round=rnd, date='2026-11-07', kickoff='15:00')


def observed(f=None, **fields):
    f = f or fixture()
    row = dict(home=f['home'], away=f['away'], date=f['date'], home_score=1, away_score=1,
               status='FT AET', winner='Home Town', decision='penalties', source_url=SOURCE)
    row.update(fields)
    return dict(fixture=f, observation=row)


def page(rnd, rows, day='Saturday 7 November 2026'):
    return f'<h1>Fixtures/Results, {scan.fwp_round_label(rnd)}, 2026-2027</h1><h3>{day}</h3><table>{rows}</table>'


def row(home, hs, ass, away, note=''):
    return f'<tr><td>FT</td><td>{home}</td><td>{hs}</td><td>{ass}</td><td>{away}</td></tr><tr><td>{note}</td></tr>'


class DecisionPolicyTests(unittest.TestCase):
    def test_one_consistent_accepted_penalty_report_is_enough(self):
        result = classify_batch([observed()], [])
        self.assertEqual(result[0]['outcome']['result']['winner'], 'Home Town')
        self.assertEqual(result[0]['outcome']['result']['decision_sources'], [SOURCE])

    def test_numerical_shootout_decision_is_preserved(self):
        result = classify_batch([observed(winner='', home_pens=5, away_pens=4)], [])
        self.assertEqual(result[0]['outcome']['result']['winner'], 'Home Town')
        self.assertEqual(result[0]['outcome']['result']['home_pens'], 5)

    def test_missing_winner_holds_only_its_fixture(self):
        clear = observed(fixture('Other Town','Next City'), home_score=3, away_score=0, winner='', decision='')
        result = classify_batch([observed(winner='', decision=''), clear], [])
        self.assertEqual(sum(bool(d.get('held')) for d in result), 1)
        self.assertEqual(sum(d.get('outcome', {}).get('kind') == 'result' for d in result), 1)

    def test_level_score_refinement_preserves_explicit_winner(self):
        result = classify_batch([observed(winner='', decision='', source_url=LIVE), observed()], [])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['outcome']['result']['winner'], 'Home Town')
        self.assertEqual(result[0]['refined_observations'], 1)

    def test_conflicting_pages_from_one_publisher_are_not_corroboration(self):
        result = classify_batch([observed(), observed(winner='Away City', source_url=LIVE)], [])
        self.assertIn('corroboration', result[0]['held'])

    def test_conflicting_shootout_scores_are_held_even_when_winner_agrees(self):
        result=classify_batch([observed(home_pens=5,away_pens=4),
                              observed(home_pens=4,away_pens=3,source_url=LIVE)],[])
        self.assertIn('conflicting shoot-out scores',result[0]['held'])

    def test_explicit_shootout_numbers_refine_a_winner_only_report(self):
        result=classify_batch([observed(),observed(home_pens=5,away_pens=4,source_url=LIVE)],[])
        self.assertEqual(result[0]['outcome']['result']['home_pens'],5)

    def test_explicit_official_decision_resolves_secondary_conflict(self):
        official = observed(source_url='https://www.thefa.com/competitions/thefacup/results')
        result = classify_batch([official, observed(winner='Away City', source_url=LIVE)], [])
        self.assertEqual(result[0]['outcome']['result']['winner'], 'Home Town')

    def test_contradictory_or_incomplete_penalties_are_held(self):
        for fields in [dict(home_score=3, away_score=2), dict(home_pens=4, away_pens=4),
                       dict(home_pens=3, away_pens=4), dict(home_pens=5),
                       dict(source_url='https://unreviewed.test/result'),
                       dict(winner='Unrelated Club')]:
            with self.subTest(fields=fields):
                self.assertTrue(classify_batch([observed(**fields)], [])[0].get('held'))

    def test_source_matching_rejects_lookalikes_and_other_competitions(self):
        for url in ['http://www.footballwebpages.co.uk/fa-cup',
                    'https://www.footballwebpages.co.uk.evil.test/fa-cup',
                    'https://www.footballwebpages.co.uk/fa-cup-other',
                    'https://www.thefa.com/not-a-competition/result']:
            self.assertFalse(publisher(url))

    def test_ordinary_qualifying_draw_keeps_its_replay_semantics(self):
        result = classify_batch([observed(fixture(rnd='Fourth Round Qualifying'), winner='', decision='')], [])
        self.assertEqual(result[0]['outcome']['result']['decision'], 'draw-replay')

    def test_conflicting_scores_do_not_leave_first_observation_publishable(self):
        first = observed(home_score=2, away_score=0, winner='', decision='')
        second = observed(home_score=0, away_score=2, winner='', decision='', source_url=LIVE)
        self.assertTrue(classify_batch([first, second], [])[0].get('held'))

    def test_canonical_date_conflict_retains_existing_result(self):
        existing = dict(observed()['observation'], round='First Round Proper', winner='Away City')
        before = copy.deepcopy(existing)
        result = classify_batch([observed()], [existing])
        self.assertTrue(result[0].get('held'))
        self.assertEqual(existing, before)

    def test_parser_retains_named_penalty_scores(self):
        raw = page('First Round Proper', row('Home Town',1,1,'Away City','Home Town win 5–4 on penalties'))
        observations = scan.parse_fwp_observations(raw, [fixture()], SOURCE)
        self.assertEqual(observations[0]['observation']['home_pens'], 5)
        self.assertEqual(observations[0]['observation']['away_pens'], 4)
        self.assertEqual(classify_batch(observations, [])[0]['outcome']['result']['winner'], 'Home Town')


class AutomaticRecoveryTests(unittest.TestCase):
    def run_results(self, data, raw, live=''):
        rnd = data['source_round']
        urls = {scan.fwp_round_url(rnd): raw, scan.FWP_LIVE_URL: live,
                'https://www.thefa.com/competitions/thefacup/results': ''}
        with tempfile.TemporaryDirectory() as tmp:
            dp,rp,cp = [Path(tmp)/name for name in ('data.json','report.json','capture.json')]
            dp.write_text(json.dumps(data))
            with patch.object(scan,'DATA',dp), patch.object(scan,'REPORT',rp), patch.object(scan,'SOURCE_CAPTURE',cp), \
                 patch.object(scan,'fetch',side_effect=lambda u:urls[u]), patch('sys.argv',['scan','--publish']):
                scan.main()
            return json.loads(dp.read_text()),json.loads(rp.read_text())

    def state(self):
        return dict(source_round='First Round Proper', source_tie_count=2,
                    fixtures=draw.fixture_map([fixture(),fixture('Other Town','Next City')]),
                    results={}, result_history={})

    def test_real_entrypoint_partial_publish_recovery_and_repeat(self):
        source = page('First Round Proper',row('Home Town',1,1,'Away City') + row('Other Town',3,0,'Next City'))
        first,report = self.run_results(self.state(),source)
        self.assertEqual(len(first['pending_match_decisions']),1)
        self.assertNotIn('Home Town',first['results'])
        self.assertEqual(first['results']['Other Town']['winner'],'Other Town')
        self.assertFalse(report['blocked'])
        repeated,_ = self.run_results(first,source)
        self.assertEqual(repeated,first)
        detailed = page('First Round Proper',row('Home Town',1,1,'Away City','Home Town win 5-4 on penalties'))
        fixed,_ = self.run_results(first,source,detailed)
        self.assertFalse(fixed['pending_match_decisions'])
        self.assertEqual(fixed['results']['Home Town']['winner'],'Home Town')
        again,_ = self.run_results(fixed,detailed)
        self.assertEqual(again,fixed)

    def test_recovery_survives_actual_draw_promotion(self):
        source = page('First Round Proper',row('Home Town',1,1,'Away City'))
        first,_ = self.run_results(self.state(),source)
        next_round = 'Second Round Proper'
        next_rows = [dict(round=next_round,home='Home Town or Away City',away='League Club',date='2026-12-05')]
        next_rows += [dict(round=next_round,home=f'Host {i}',away=f'Visitor {i}',date='2026-12-05') for i in range(1,20)]
        with tempfile.TemporaryDirectory() as tmp:
            dp,rp = Path(tmp)/'data.json',Path(tmp)/'report.json'
            dp.write_text(json.dumps(first))
            with patch.object(draw,'DATA',dp),patch.object(draw,'REPORT',rp),patch.object(draw,'fetch',return_value='html'), \
                 patch.object(draw,'parse_page',return_value=next_rows),patch('sys.argv',['draw','--publish','--max-pages','1']):
                draw.main()
            promoted = json.loads(dp.read_text())
        self.assertEqual(promoted['pending_match_decisions'],first['pending_match_decisions'])
        before = copy.deepcopy(promoted)
        later = page('First Round Proper',row('Home Town',1,1,'Away City','Home Town win 5-4 on penalties'))
        fixed,report = retry_archived_holds(promoted,lambda u:later)
        self.assertEqual(report['recovered'],1)
        self.assertFalse(fixed['pending_match_decisions'])
        self.assertEqual(fixed['fixtures']['Home Town']['home'],'Home Town')
        self.assertEqual(fixed['round_fixtures'],before['round_fixtures'])
        self.assertEqual(promoted,before)

    def test_archived_source_failure_preserves_hold(self):
        source = page('First Round Proper',row('Home Town',1,1,'Away City'))
        first,_ = self.run_results(self.state(),source)
        first['round_fixtures']={'First Round Proper':draw.fixture_values(first['fixtures'])}
        first['source_round']='Second Round Proper'
        before=copy.deepcopy(first)
        def unavailable(_): raise OSError('source offline')
        candidate,report=retry_archived_holds(first,unavailable)
        self.assertEqual(candidate,before)
        self.assertTrue(report['source_failures'])

    def test_missing_canonical_ancestry_remains_global_failure(self):
        data=self.state()
        retain_holds(data,classify_batch([observed(winner='',decision='')],[]))
        data['source_round']='Second Round Proper'
        with self.assertRaisesRegex(ValueError,'unique canonical archived fixture'):
            retry_archived_holds(data,lambda _: '')

    def test_health_reports_pending_decision_without_blocking_other_results(self):
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'competition.json').read_text())
        data['replays']={}  # Isolate this hold from unrelated live replay schedules.
        fixtures=draw.fixture_values(data['fixtures'])
        held_fixture=fixtures[0]
        held_fixture['date']='2020-01-01'
        data['fixtures']=draw.fixture_map(fixtures)
        data['pending_match_decisions']=[dict(fixture=held_fixture,date='2020-01-01',
            reason='completed level fixture awaiting penalty decision',state='awaiting-decision',
            sources=[SOURCE],first_seen_at='2020-01-01T20:00:00+00:00')]
        with tempfile.TemporaryDirectory() as tmp:
            destination=Path(tmp)
            (destination/'updater').mkdir()
            script=destination/'updater/competition_health.py'
            script.write_text((root/'updater/competition_health.py').read_text())
            (destination/'competition.json').write_text(json.dumps(data))
            env={**os.environ,'TFFC_FIXTURE_LOCAL_HEALTH':'0'}
            result=subprocess.run([sys.executable,str(script)],env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report=json.loads((destination/'updater/competition-health.json').read_text())
            self.assertEqual(report['data_state'],'pending-decisions')
            self.assertTrue(report['pending_match_decisions'])
            self.assertIn('Match decision still unresolved',result.stdout)
            data.pop('pending_match_decisions')
            (destination/'competition.json').write_text(json.dumps(data))
            result=subprocess.run([sys.executable,str(script)],env=env,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0,'untracked overdue fixtures must still fail health')
