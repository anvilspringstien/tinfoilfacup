"""Permanent incident rejection tests, including the repaired historical guards."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from round_transition_fixture import ROOT, frozen, draw, import_draw, resolve_replays
from run_round_transition_rehearsal import write_state, publication_commands
from stage_preceding_replay_candidates import draw_matches, stage


class DrawTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = frozen('competition-before.json.gz')
        cls.published = frozen('competition-published.json.gz')

    def test_incomplete_and_oversized_real_draw_reject_without_writing(self):
        rows = draw.fixture_values(self.published['fixtures'])
        extra = dict(rows[-1], home='Synthetic Extra Home', away='Synthetic Extra Away')
        before = copy.deepcopy(self.before)
        for changed in (rows[:-1], rows + [extra]):
            with self.subTest(ties=len(changed)), self.assertRaisesRegex(SystemExit, 'expected 40 First Round Proper ties'):
                import_draw(self.before, changed)
        self.assertEqual(self.before, before)

    def test_duplicate_club_rejects_complete_sized_draw(self):
        rows = draw.fixture_values(self.published['fixtures'])
        rows[-1] = dict(rows[-1], home=rows[0]['home'])
        with self.assertRaisesRegex(SystemExit, 'concrete clubs appear in more than one'):
            import_draw(self.before, rows)

    def test_wrong_round_source_cannot_promote_or_mutate_input(self):
        rows = [dict(row, round='Second Round Proper')
                for row in draw.fixture_values(self.published['fixtures'])]
        with self.assertRaisesRegex(SystemExit, 'active-round fixture catalogue is incomplete'):
            import_draw(self.before, rows)

    def test_all_22_possible_replay_winners_have_one_destination(self):
        for replay in draw.fixture_values(self.before['replays']):
            if replay['round'] != 'Fourth Round Qualifying Replay':
                continue
            for winner in (replay['home'], replay['away']):
                with self.subTest(winner=winner):
                    destinations = draw_matches(self.published, winner)
                    self.assertEqual(len(destinations), 1, winner)
                    options = [side for f in destinations for key in ('home', 'away')
                               for side in draw.alternatives(f[key])]
                    self.assertEqual(sum(draw.compatible(option, winner) for option in options), 1)

    def test_alias_is_identity_only_and_ambiguous_destination_stays_blocked(self):
        self.assertTrue(draw.compatible('Forest Grn', 'Forest Green Rovers'))
        self.assertFalse(draw.compatible('Forest Grn', 'Forest Green City'))
        # Existing shared identity aliases must survive the matcher change.
        aliased = dict(fixtures={'x': dict(home='Sutton United Birmingham',
                                         away='Next Club', date='2026-11-07')})
        self.assertEqual(len(draw_matches(aliased, 'Sutton United West Midlands')), 1)
        source = copy.deepcopy(self.published)
        source['fixtures']['Synthetic Collision'] = dict(round='First Round Proper',
            home='Anstey Nomads', away='Synthetic Opponent', date='2026-11-07')
        replay = next(r for r in draw.fixture_values(self.before['replays']) if r['home'] == 'Anstey Nomads')
        result = dict(replay, home_score=2, away_score=0, winner=replay['home'], status='FT')
        before = copy.deepcopy(source)
        with self.assertRaisesRegex(ValueError, 'no unique next-round draw'):
            stage(source, dict(production_mutation=False, blocked=[], replay_candidates=[result]))
        self.assertEqual(source, before)

    def test_real_pending_replays_resolve_for_either_winning_side(self):
        for home_wins in (True, False):
            with self.subTest(home_wins=home_wins):
                resolved = resolve_replays(self.published, home_wins)
                self.assertEqual(len(draw.fixture_values(resolved['fixtures'])), 40)
                self.assertEqual(resolved['round_fixtures'], self.published['round_fixtures'])
                self.assertEqual(resolved['replays'], self.published['replays'])
                for club, history in self.published['result_history'].items():
                    for result in history:
                        self.assertIn(result, resolved['result_history'][club])

    def test_rehearsal_includes_both_publication_workflows_and_beta(self):
        commands = publication_commands()
        for script in ('clubfinder_render', 'clubfinder_stats', 'historical_journey',
                       'historical_venue', 'journey_integrity', 'production_ui'):
            self.assertIn(['node', 'updater/' + script + '_regression.js'], commands)
        self.assertIn([sys.executable, 'updater/unicorn_replay_regression.py'], commands)
        self.assertIn(['node', 'tests/test_beta_thame_next_fixture.js'], commands)


class RepairedGuardRejectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='tffc-guard-rejections-')
        cls.destination = Path(cls.temporary.name) / 'repo'
        shutil.copytree(ROOT, cls.destination, ignore=shutil.ignore_patterns('.git', '__pycache__', 'node_modules', 'assets'))
        cls.valid = frozen('competition-published.json.gz')

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def checks(self):
        return [
            [sys.executable, 'updater/unicorn_replay_regression.py'],
            ['node', 'tests/test_production_thame_next_fixture.js'],
            ['node', 'tests/test_beta_thame_next_fixture.js'],
            [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_beta_embedded_snapshot_refresh.py'],
        ]

    def test_repaired_guards_accept_real_promoted_state(self):
        write_state(self.destination, self.valid)
        for command in self.checks():
            with self.subTest(command=command):
                result = subprocess.run(command, cwd=self.destination, capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_each_repaired_guard_rejects_missing_archive_partial_or_wrong_round(self):
        for damage in ('missing-archive', 'partial-active', 'wrong-round'):
            data = copy.deepcopy(self.valid)
            if damage == 'missing-archive':
                data['round_fixtures']['Fourth Round Qualifying'].pop()
            else:
                fixtures = draw.fixture_values(data['fixtures'])
                if damage == 'partial-active':
                    fixtures.pop()
                else:
                    fixtures[0]['round'] = 'Second Round Proper'
                data['fixtures'] = draw.fixture_map(fixtures)
            write_state(self.destination, data)
            for command in self.checks():
                with self.subTest(damage=damage, command=command):
                    result = subprocess.run(command, cwd=self.destination, capture_output=True, text=True, timeout=60)
                    self.assertNotEqual(result.returncode, 0, 'Guard accepted ' + damage)
                    output = result.stdout + result.stderr
                    # Reject for the intended invariant, not a broken stub/import.
                    self.assertRegex(output, {
                        'missing-archive': r'32 unique ties|retain exactly 32|31 != 32',
                        'partial-active': r'canonical number|declared tie count|39 != 40',
                        'wrong-round': r'declared current round|False is not true',
                    }[damage])


if __name__ == '__main__':
    unittest.main()
