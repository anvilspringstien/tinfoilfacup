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
    return {"production_mutation": False, "replay_candidates": rows, "blocked": [],
            "observations": 13, "already_recorded": 0, "events": [],
            "scheduled_replay_gaps": [
                {"home": row["home"], "away": row["away"],
                 "date": row["date"], "source_observed": True} for row in rows]}


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
        with self.assertRaisesRegex(ValueError, "not fully accounted"):
            readiness(source)


    def test_thirteen_recorded_and_one_new_thame_replay(self):
        thame = {"home": "Exmouth Town", "away": "Thame United",
                 "date": "2026-09-23", "round": "Second Round Qualifying Replay",
                 "winner": "Thame United", "home_score": 1, "away_score": 3,
                 "status": "FT", "decision": ""}
        report = {"production_mutation": False, "replay_candidates": [thame],
                  "blocked": [], "events": [], "observations": 14,
                  "already_recorded": 13,
                  "scheduled_replay_gaps": [
                      {"home": thame["home"], "away": thame["away"],
                       "date": thame["date"], "source_observed": True}]}
        result = readiness(report)
        self.assertEqual((result["approved_count"], result["held_count"]), (1, 0))
        self.assertEqual(result["already_recorded"], 13)
        self.assertEqual(result["approved"][0]["winner"], "Thame United")

    def test_same_source_count_cannot_hide_unseen_thame(self):
        report = audit()
        report["scheduled_replay_gaps"].append(
            {"home": "Exmouth Town", "away": "Thame United",
             "date": "2026-09-23", "source_observed": False})
        with self.assertRaisesRegex(ValueError, "absent from source"):
            readiness(report)

    def test_observed_thame_cannot_pass_before_staging(self):
        report = audit()
        report["scheduled_replay_gaps"].append(
            {"home": "Exmouth Town", "away": "Thame United",
             "date": "2026-09-23", "source_observed": True})
        with self.assertRaisesRegex(ValueError, "no source-backed result"):
            readiness(report)

    def test_duplicate_candidate_fails_closed(self):
        report = audit()
        report["replay_candidates"].append(dict(report["replay_candidates"][0]))
        report["observations"] += 1
        with self.assertRaisesRegex(ValueError, "duplicate replay candidate"):
            readiness(report)

    def test_all_already_published_is_clean_noop(self):
        report = {"production_mutation": False, "replay_candidates": [],
                  "blocked": [], "events": [], "observations": 14,
                  "already_recorded": 14, "scheduled_replay_gaps": []}
        result = readiness(report)
        self.assertEqual((result["approved_count"], result["held_count"]), (0, 0))
        self.assertEqual(result["status"], "ready")


if __name__ == "__main__":
    unittest.main()
