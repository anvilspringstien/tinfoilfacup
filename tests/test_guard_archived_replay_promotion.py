import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "updater"))
from guard_archived_replay_promotion import readiness


def audit():
    rows = [{"home": "Club " + str(i), "away": "Opponent " + str(i),
             "date": "2026-09-22", "round": "Second Round Qualifying Replay",
             "winner": "Club " + str(i), "decision": "normal",
             "home_score": 2, "away_score": 1} for i in range(12)]
    rows.append({"home": "Wimborne Town", "away": "Weston-super-Mare",
                 "date": "2026-09-22", "round": "Second Round Qualifying Replay",
                 "winner": "Wimborne Town", "decision": "penalties",
                 "home_score": 1, "away_score": 1})
    return {"production_mutation": False, "replay_candidates": rows, "blocked": []}


def evidence():
    return {"2026-09-22|weston-super-mare|wimborne town": [
        {"domain": domain, "url": url, "home": "Wimborne Town",
         "away": "Weston-super-Mare", "date": "2026-09-22",
         "home_score": 1, "away_score": 1, "home_pens": 4, "away_pens": 3,
         "winner": "Wimborne Town", "decision": "penalties"}
        for domain, url in [
            ("thefa.com", "https://www.thefa.com/match-report"),
            ("wimbornetownfc.co.uk", "https://www.wimbornetownfc.co.uk/match-report")]]}


class ReadinessTests(unittest.TestCase):
    def test_uncorroborated_penalties_held_other_twelve_approved(self):
        source = audit()
        original = copy.deepcopy(source)
        result = readiness(source)
        self.assertEqual((result["approved_count"], result["held_count"]), (12, 1))
        self.assertEqual(source, original)

    def test_two_independent_matching_publishers_approve_thirteen(self):
        result = readiness(audit(), evidence())
        self.assertEqual((result["approved_count"], result["held_count"]), (13, 0))

    def test_one_publisher_does_not_approve_penalties(self):
        reports = evidence()
        key = next(iter(reports))
        reports[key] = reports[key][:1]
        self.assertEqual(readiness(audit(), reports)["held_count"], 1)

    def test_conflicting_penalty_winner_is_held(self):
        reports = evidence()
        key = next(iter(reports))
        for item in reports[key]:
            item.update({"home_pens": 3, "away_pens": 4, "winner": "Weston-super-Mare"})
        self.assertEqual(readiness(audit(), reports)["held_count"], 1)

    def test_missing_fixture_fails_closed(self):
        source = audit()
        source["replay_candidates"].pop()
        with self.assertRaisesRegex(ValueError, "all 13"):
            readiness(source)


if __name__ == "__main__":
    unittest.main()
