"""Regression cases for read-only preceding-round replay auditing."""
import copy
import sys
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

    def test_missing_archive_fails_closed(self):
        data = fixture_data()
        data["round_fixtures"] = {}
        with self.assertRaisesRegex(ValueError, "archive missing"):
            audit.audit(data, "<html/>")


if __name__ == "__main__":
    unittest.main()
