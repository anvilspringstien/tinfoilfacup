import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "updater"))
from quarantined_campaign_view import campaign_view


class QuarantinedCampaignTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            "current_custodian": "Weston-super-Mare",
            "pigeon_miles_flown": 169,
            "matches_played": 4,
            "goals_seen": 18,
            "grounds_visited": 4,
            "history": [{"round": "First Round Qualifying", "verified": True}],
        }
        self.quarantine = {
            "home": "Wimborne Town", "away": "Weston-super-Mare",
            "date": "2026-09-22", "round": "Second Round Qualifying Replay",
            "reason": "conflicting penalty score",
        }

    def test_weston_waits_without_losing_verified_progress(self):
        view = campaign_view(self.snapshot, self.quarantine)
        for key in self.snapshot:
            self.assertEqual(view[key], self.snapshot[key])
        self.assertEqual(view["verification_notice"]["status"], "awaiting_verification")
        self.assertNotIn("winner", view["verification_notice"])
        self.assertNotIn("new_custodian", view["verification_notice"])

    def test_normal_campaign_unaffected(self):
        view = campaign_view(self.snapshot)
        self.assertEqual(view["verification_notice"], None)
        self.assertEqual(view["pigeon_miles_flown"], 169)

    def test_no_mutation_of_original_snapshot(self):
        campaign_view(self.snapshot, self.quarantine)["history"].append({"fake": True})
        self.assertEqual(len(self.snapshot["history"]), 1)


if __name__ == "__main__":
    unittest.main()
