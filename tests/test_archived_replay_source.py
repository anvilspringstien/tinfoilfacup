"""Dedicated preceding-round replay source must never resolve to original ties."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "updater"))
import audit_preceding_round_replays as audit


class ReplaySourceTests(unittest.TestCase):
    def test_replay_endpoint_distinct_from_original(self):
        url = audit.archived_replay_source("Second Round Qualifying")
        self.assertTrue(url.endswith("/second-qualifying-round-replay"))
        self.assertNotEqual(url, audit.scan.fwp_round_url("Second Round Qualifying"))

    def test_original_round_page_fails_closed(self):
        original = "<h1>Fixtures/Results, Second Qualifying Round, 2026-2027</h1>"
        with self.assertRaises(SystemExit):
            audit.validate_archived_replay_page(
                original, "Second Round Qualifying", audit.archived_replay_source("Second Round Qualifying"))

    def test_replay_round_page_accepted(self):
        replay = "<h1>Fixtures/Results, Second Qualifying Round Replay, 2026-2027</h1>"
        audit.validate_archived_replay_page(
            replay, "Second Round Qualifying", audit.archived_replay_source("Second Round Qualifying"))


if __name__ == "__main__":
    unittest.main()
