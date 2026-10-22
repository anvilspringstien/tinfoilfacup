"""Read-only archived replay promotion preview regression."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "updater"))
import preview_preceding_replay_promotion as preview
import audit_preceding_round_replays as audit
from test_preceding_round_replay_audit import fixture_data


class PreviewTests(unittest.TestCase):
    def test_wimborne_candidate_updates_copy_not_production(self):
        original = fixture_data()
        before = copy.deepcopy(original)
        replay = {"home": "Wimborne Town", "away": "Weston-super-Mare",
                  "home_score": 1, "away_score": 1, "winner": "Wimborne Town",
                  "status": "FT AET", "decision": "penalties", "date": "2026-09-22",
                  "round": "Second Round Qualifying Replay"}
        report = {"archived_round": "Second Round Qualifying", "observations": 1,
                  "replay_candidates": [replay], "already_recorded": [], "blocked": []}
        with patch.object(audit, "audit", return_value=report):
            result = preview.preview(original, "<html/>")
        self.assertEqual(original, before)
        self.assertFalse(result["production_mutation"])
        self.assertEqual(len(result["publishable"]), 1)
        self.assertEqual(result["candidate_data"]["results"]["Wimborne Town"]["winner"],
                         "Wimborne Town")

    def test_quarantine_does_not_block_independent_healthy_fixture(self):
        original = fixture_data()
        replay = {"home": "Crowborough Athletic", "away": "Hampton & Richmond Borough",
                  "home_score": 3, "away_score": 1, "winner": "Crowborough Athletic",
                  "status": "FT", "date": "2026-09-22",
                  "round": "Second Round Qualifying Replay"}
        report = {"archived_round": "Second Round Qualifying", "observations": 2,
                  "replay_candidates": [replay], "already_recorded": [],
                  "blocked": [{"home": "Wimborne Town", "away": "Weston-super-Mare",
                               "reason": "penalty decision with non-level source score"}]}
        with patch.object(audit, "audit", return_value=report):
            result = preview.preview(original, "<html/>")
        self.assertEqual(len(result["publishable"]), 1)
        self.assertEqual(len(result["quarantined"]), 1)
        self.assertEqual(original.get("results"), None)


if __name__ == "__main__":
    unittest.main()
