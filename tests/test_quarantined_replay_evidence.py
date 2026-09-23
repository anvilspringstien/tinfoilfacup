import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "updater"))
from reconcile_quarantined_replay_evidence import reconcile

BLOCKED = {"home":"Wimborne Town","away":"Weston-super-Mare","date":"2026-09-22",
           "reason":"penalty decision with non-level source score: independent verification required"}
BASE = {"home":"Wimborne Town","away":"Weston-super-Mare","date":"2026-09-22",
        "home_score":1,"away_score":1,"home_pens":4,"away_pens":3,
        "winner":"Wimborne Town","decision":"penalties"}
def source(domain):
    return dict(BASE, domain=domain, url="https://"+domain+"/match-report")

class QuarantineRecoveryTests(unittest.TestCase):
    def test_no_source_stays_quarantined(self):
        self.assertEqual(reconcile(BLOCKED, [])["status"], "quarantined")
    def test_one_source_not_enough(self):
        self.assertEqual(reconcile(BLOCKED, [source("thefa.com")])["status"], "quarantined")
    def test_two_independent_agree(self):
        result = reconcile(BLOCKED, [source("thefa.com"),source("wimbornetownfc.co.uk")])
        self.assertEqual(result["status"], "independently_verified")
        self.assertFalse(result["production_mutation"])
    def test_conflicting_penalties_stay_quarantined(self):
        second = source("wimbornetownfc.co.uk")
        second["home_pens"] = 5
        self.assertEqual(reconcile(BLOCKED, [source("thefa.com"),second])["status"], "quarantined")
    def test_inconsistent_extra_time_score_rejected(self):
        second = source("wimbornetownfc.co.uk")
        second["home_score"] = 3
        self.assertEqual(reconcile(BLOCKED, [source("thefa.com"),second])["status"], "quarantined")
    def test_untrusted_source_rejected(self):
        self.assertEqual(reconcile(BLOCKED,[source("thefa.com"),source("example.com")])["status"],"quarantined")
    def test_wrong_fixture_rejected(self):
        second = source("wimbornetownfc.co.uk")
        second["away"] = "Different Club"
        self.assertEqual(reconcile(BLOCKED,[source("thefa.com"),second])["status"],"quarantined")
if __name__ == "__main__":
    unittest.main()
