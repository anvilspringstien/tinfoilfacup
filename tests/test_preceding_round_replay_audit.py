"""Regression cases for read-only preceding-round replay auditing."""
import copy
import sys
from datetime import datetime
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "updater"))
import audit_preceding_round_replays as audit
import auto_round_results as scan


def fixture_data():
    original = {"home": "Weston-super-Mare", "away": "Wimborne Town",
                "home_score": 1, "away_score": 1, "winner": "",
                "status": "FT", "decision": "draw-replay", "date": "2026-09-19",
                "round": "Second Round Qualifying"}
    return {"source_round": "Third Round Qualifying",
            "round_fixtures": {"Second Round Qualifying": {
                "Weston-super-Mare": {"home": "Weston-super-Mare",
                                       "away": "Wimborne Town",
                                       "round": "Second Round Qualifying"}}},
            "result_history": {"Weston-super-Mare": [original]},
            "fixtures": {"Wimborne": {"home": "Hamp & Rich or Crowborough",
                                      "away": "Weston SM or Wimborne",
                                      "round": "Third Round Qualifying"}}}


class PrecedingReplayAuditTests(unittest.TestCase):
    def test_cross_page_penalty_note_is_one_held_fixture(self):
        from guard_archived_replay_promotion import readiness
        data = fixture_data()
        data['replays'] = {'Weston': {
            'round': 'Second Round Qualifying Replay', 'home': 'Wimborne Town',
            'away': 'Weston-super-Mare', 'date': '2026-09-22'}}
        fixture = data['round_fixtures']['Second Round Qualifying']['Weston-super-Mare']
        plain = {'fixture': fixture, 'observation': {
            'home': 'Wimborne Town', 'away': 'Weston-super-Mare',
            'home_score': 1, 'away_score': 1, 'winner': '', 'decision': '',
            'date': '2026-09-22', 'status': 'FT', 'source_url': 'https://example.test/replays'}}
        detailed = copy.deepcopy(plain)
        detailed['observation'].update(winner='Wimborne Town', decision='penalties',
                                       source_url='https://example.test/live')
        before = copy.deepcopy(data)
        with patch.object(scan, 'parse_fwp_observations', side_effect=[[plain], [detailed]]):
            report = audit.audit(data, '<html/>', '<html/>')
        self.assertEqual((report['source_observations'], report['observations']), (2, 1))
        self.assertEqual(len(report['penalty_refinements']), 1)
        self.assertFalse(report['blocked'])
        gate = readiness(report)
        self.assertEqual((gate['approved_count'], gate['held_count']), (0, 1))
        self.assertEqual(data, before)

    def test_penalty_refinement_never_erases_material_disagreement(self):
        fixture = fixture_data()['round_fixtures']['Second Round Qualifying']['Weston-super-Mare']
        plain = {'fixture': fixture, 'observation': {
            'home': 'Wimborne Town', 'away': 'Weston-super-Mare',
            'home_score': 1, 'away_score': 1, 'winner': '', 'decision': '',
            'date': '2026-09-22', 'status': 'FT', 'source_url': 'https://example.test/replays'}}
        detailed = copy.deepcopy(plain)
        detailed['observation'].update(winner='Wimborne Town', decision='penalties',
                                       source_url='https://example.test/live')
        for change in ({'home_score': 2}, {'date': '2026-09-23'},
                       {'home': 'Weston-super-Mare', 'away': 'Wimborne Town'},
                       {'source_url': 'https://example.test/replays'},
                       {'winner': 'Unrelated Town'}):
            with self.subTest(change=change):
                other = copy.deepcopy(detailed)
                other['observation'].update(change)
                rows, refinements = audit.reconcile_penalty_refinements([plain, other])
                self.assertEqual(rows, [plain, other])
                self.assertFalse(refinements)
        conflicting = copy.deepcopy(detailed)
        conflicting['observation'].update(winner='Weston-super-Mare', source_url='https://example.test/third')
        rows, refinements = audit.reconcile_penalty_refinements([plain, detailed, conflicting])
        self.assertEqual(len(rows), 3)
        self.assertFalse(refinements)

    def test_wimborne_penalties_progress_only_with_explicit_winner(self):
        data = fixture_data()
        before = copy.deepcopy(data)
        obs = {"fixture": data["round_fixtures"]["Second Round Qualifying"]["Weston-super-Mare"],
               "observation": {"home": "Wimborne Town", "away": "Weston-super-Mare",
                               "home_score": 1, "away_score": 1, "winner": "Wimborne Town",
                               "status": "FT AET", "decision": "penalties",
                               "date": "2026-09-22"}}
        with patch.object(scan, "parse_fwp_observations", return_value=[obs]):
            report = audit.audit(data, "<html/>")
        self.assertEqual(len(report["replay_candidates"]), 1)
        row = report["replay_candidates"][0]
        self.assertEqual((row["round"], row["winner"], row["decision"]),
                         ("Second Round Qualifying Replay", "Wimborne Town", "penalties"))
        self.assertEqual((row["home_score"], row["away_score"]), (1, 1))
        self.assertEqual(data, before)
        self.assertFalse(report["production_mutation"])

    def test_level_replay_without_winner_is_blocked(self):
        data = fixture_data()
        obs = {"fixture": data["round_fixtures"]["Second Round Qualifying"]["Weston-super-Mare"],
               "observation": {"home": "Wimborne Town", "away": "Weston-super-Mare",
                               "home_score": 1, "away_score": 1, "winner": "",
                               "status": "FT AET", "date": "2026-09-22"}}
        with patch.object(scan, "parse_fwp_observations", return_value=[obs]):
            report = audit.audit(data, "<html/>")
        self.assertFalse(report["replay_candidates"])
        self.assertEqual(len(report["blocked"]), 1)

    def test_real_fwp_wimborne_penalty_score_discrepancy_quarantined(self):
        data = fixture_data()
        obs = {"fixture": data["round_fixtures"]["Second Round Qualifying"]["Weston-super-Mare"],
               "observation": {"home": "Wimborne Town", "away": "Weston-super-Mare",
                               "home_score": 3, "away_score": 2,
                               "winner": "Wimborne Town", "decision": "penalties",
                               "status": "FT", "date": "2026-09-22"}}
        with patch.object(scan, "parse_fwp_observations", return_value=[obs]):
            report = audit.audit(data, "<html/>")
        self.assertFalse(report["replay_candidates"])
        self.assertEqual(len(report["blocked"]), 1)
        self.assertIn("independent verification", report["blocked"][0]["reason"])

    def test_already_recorded_replay_is_a_duplicate(self):
        data = fixture_data()
        recorded = {"round": "Second Round Qualifying Replay",
                    "home": "Wimborne Town", "away": "Weston-super-Mare",
                    "home_score": 1, "away_score": 1,
                    "winner": "Wimborne Town", "decision": "penalties",
                    "status": "FT AET", "date": "2026-09-22"}
        data["result_history"]["Wimborne Town"] = [recorded]
        before = copy.deepcopy(data)
        obs = {"fixture": data["round_fixtures"]["Second Round Qualifying"]["Weston-super-Mare"],
               "observation": dict(recorded)}
        with patch.object(scan, "parse_fwp_observations", return_value=[obs]):
            report = audit.audit(data, "<html/>")
        self.assertEqual(report["observations"], 1)
        self.assertEqual(report["already_recorded"], 1)
        self.assertFalse(report["replay_candidates"])
        self.assertFalse(report["blocked"])
        self.assertFalse(report["production_mutation"])
        self.assertEqual(data, before)

    def test_scheduled_replay_gap_is_not_hidden_by_source_count(self):
        data = fixture_data()
        data["replays"] = {"Exmouth Town": {
            "round": "Second Round Qualifying Replay",
            "home": "Exmouth Town", "away": "Thame United",
            "date": "2026-09-23"}}
        with patch.object(scan, "parse_fwp_observations", return_value=[]):
            report = audit.audit(data, "<html/>")
        self.assertEqual(len(report["scheduled_replay_gaps"]), 1)
        self.assertEqual(report["scheduled_replay_gaps"][0]["home"], "Exmouth Town")
        self.assertFalse(report["scheduled_replay_gaps"][0]["source_observed"])
        self.assertFalse(report["production_mutation"])

    def test_scheduled_replay_requires_published_not_candidate_result(self):
        data = fixture_data()
        data["replays"] = {"Weston": {
            "round": "Second Round Qualifying Replay",
            "home": "Wimborne Town", "away": "Weston-super-Mare",
            "date": "2026-09-22"}}
        obs = {"fixture": data["round_fixtures"]["Second Round Qualifying"]["Weston-super-Mare"],
               "observation": {"home": "Wimborne Town", "away": "Weston-super-Mare",
                               "home_score": 1, "away_score": 1, "winner": "Wimborne Town",
                               "status": "FT AET", "decision": "penalties",
                               "date": "2026-09-22"}}
        with patch.object(scan, "parse_fwp_observations", return_value=[obs]):
            report = audit.audit(data, "<html/>")
        self.assertEqual(len(report["replay_candidates"]), 1)
        self.assertEqual(len(report["scheduled_replay_gaps"]), 1)
        self.assertTrue(report["scheduled_replay_gaps"][0]["source_observed"])

    def test_future_scheduled_replay_is_not_a_publication_gap(self):
        data = fixture_data()
        data["replays"] = {"Future": {
            "round": "Second Round Qualifying Replay",
            "home": "Future Town", "away": "Tomorrow United",
            "date": "2026-10-06"}}
        with patch.object(scan, "parse_fwp_observations", return_value=[]):
            report = audit.audit(data, "<html/>", as_of=audit.date(2026, 10, 5))
        self.assertFalse(report["scheduled_replay_gaps"])

    def test_same_day_replay_before_kickoff_is_not_a_publication_gap(self):
        data = fixture_data()
        data["replays"] = {"Today": {
            "round": "Second Round Qualifying Replay",
            "home": "Due Town", "away": "Today United",
            "date": "2026-10-06", "kickoff": "19:45"}}
        with patch.object(scan, "parse_fwp_observations", return_value=[]):
            report = audit.audit(
                data, "<html/>",
                as_of=datetime(2026, 10, 6, 10, 33, tzinfo=audit.UK_TZ))
        self.assertFalse(report["scheduled_replay_gaps"])

    def test_same_day_replay_during_completion_grace_is_not_a_publication_gap(self):
        data = fixture_data()
        data["replays"] = {"Today": {
            "round": "Second Round Qualifying Replay",
            "home": "Due Town", "away": "Today United",
            "date": "2026-10-06", "kickoff": "19:45"}}
        with patch.object(scan, "parse_fwp_observations", return_value=[]):
            report = audit.audit(
                data, "<html/>",
                as_of=datetime(2026, 10, 6, 22, 30, tzinfo=audit.UK_TZ))
        self.assertFalse(report["scheduled_replay_gaps"])

    def test_same_day_replay_after_completion_grace_is_a_publication_gap(self):
        data = fixture_data()
        data["replays"] = {"Due": {
            "round": "Second Round Qualifying Replay",
            "home": "Due Town", "away": "Today United",
            "date": "2026-10-06", "kickoff": "19:45"}}
        with patch.object(scan, "parse_fwp_observations", return_value=[]):
            report = audit.audit(
                data, "<html/>",
                as_of=datetime(2026, 10, 6, 23, 50, tzinfo=audit.UK_TZ))
        self.assertEqual(len(report["scheduled_replay_gaps"]), 1)

    def test_same_day_replay_without_kickoff_waits_until_next_day(self):
        data = fixture_data()
        data["replays"] = {"Today": {
            "round": "Second Round Qualifying Replay",
            "home": "Due Town", "away": "Today United",
            "date": "2026-10-06"}}
        with patch.object(scan, "parse_fwp_observations", return_value=[]):
            report = audit.audit(
                data, "<html/>",
                as_of=datetime(2026, 10, 6, 23, 59, tzinfo=audit.UK_TZ))
        self.assertFalse(report["scheduled_replay_gaps"])
        with patch.object(scan, "parse_fwp_observations", return_value=[]):
            report = audit.audit(
                data, "<html/>",
                as_of=datetime(2026, 10, 7, 0, 1, tzinfo=audit.UK_TZ))
        self.assertEqual(len(report["scheduled_replay_gaps"]), 1)

    def test_missing_archive_fails_closed(self):
        data = fixture_data()
        data["round_fixtures"] = {}
        with self.assertRaisesRegex(ValueError, "archive missing"):
            audit.audit(data, "<html/>")


if __name__ == "__main__":
    unittest.main()
