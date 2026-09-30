"""In-memory archived replay staging never mutates production input."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "updater"))
import stage_preceding_replay_candidates as stage


def data():
    return {
        "fixtures": {"Wimborne": {"home":"Hamp & Rich or Crowborough",
                                   "away":"Weston SM or Wimborne","date":"2026-10-03"}},
        "result_history": {"Weston-super-Mare": [{
            "home":"Weston-super-Mare","away":"Wimborne Town",
            "home_score":1,"away_score":1,"winner":"",
            "status":"FT","decision":"draw-replay",
            "round":"Second Round Qualifying","date":"2026-09-19"}]},
        "results": {}
    }


def report():
    return {"production_mutation":False,"blocked":[],
            "replay_candidates":[{
                "home":"Wimborne Town","away":"Weston-super-Mare",
                "home_score":1,"away_score":1,"winner":"Wimborne Town",
                "decision":"penalties","status":"FT (AET)",
                "round":"Second Round Qualifying Replay","date":"2026-09-22"}]}


class StageTests(unittest.TestCase):
    def test_stage_one_verified_replay_without_input_mutation(self):
        source = data()
        original = copy.deepcopy(source)
        summary, candidate = stage.stage(source, report())
        self.assertEqual(source, original)
        self.assertEqual(summary["staged_count"], 1)
        self.assertEqual(summary["staged"][0]["winner"], "Wimborne Town")
        self.assertEqual(candidate["results"]["Wimborne Town"]["decision"], "penalties")

    def test_unexpected_source_conflict_fails_closed(self):
        r = report()
        r["blocked"] = [{"home":"Other Club","away":"Opponent","reason":"conflict"}]
        with self.assertRaisesRegex(ValueError,"unexpected source conflict"):
            stage.stage(data(), r)

    def test_no_next_round_draw_fails_closed(self):
        d = data()
        d["fixtures"] = {}
        with self.assertRaisesRegex(ValueError,"no unique next-round draw"):
            stage.stage(d, report())

    def test_thame_replay_maps_to_abbreviated_third_qualifying_draw(self):
        source = data()
        source["result_history"] = {"Thame United": [{
            "home": "Thame United", "away": "Exmouth Town",
            "home_score": 3, "away_score": 3, "winner": "",
            "status": "FT", "decision": "draw-replay",
            "round": "Second Round Qualifying", "date": "2026-09-19"}]}
        source["fixtures"] = {"Thame": {
            "home": "Thame Utd", "away": "Eastbourne Borough",
            "date": "2026-10-03", "round": "Third Round Qualifying"}}
        replay = {"home": "Exmouth Town", "away": "Thame United",
                  "home_score": 1, "away_score": 3,
                  "winner": "Thame United", "status": "FT",
                  "round": "Second Round Qualifying Replay", "date": "2026-09-23"}
        before = copy.deepcopy(source)
        summary, candidate = stage.stage(source, {
            "production_mutation": False, "blocked": [], "replay_candidates": [replay]})
        self.assertEqual(source, before)
        self.assertEqual(summary["staged_count"], 1)
        self.assertEqual(summary["staged"][0]["next_fixture"], "Thame Utd v Eastbourne Borough")
        self.assertEqual(candidate["results"]["Thame United"]["winner"], "Thame United")

    def test_reviewed_voided_result_can_stage_ordered_full_replay(self):
        source = data()
        source["result_history"] = {"Woodford Town": [{
            "home": "Woodford Town", "away": "Mulbarton Wanderers",
            "home_score": 1, "away_score": 2, "winner": "Mulbarton Wanderers",
            "status": "FT", "decision": "",
            "round": "Second Round Qualifying", "date": "2026-09-19"}]}
        source["fixtures"] = {"Mulbarton": {
            "home": "Mulbarton Wanderers", "away": "Gloucester City",
            "date": "2026-10-03", "round": "Third Round Qualifying"}}
        replay = {"home": "Mulbarton Wanderers", "away": "Woodford Town",
                  "home_score": 2, "away_score": 0,
                  "winner": "Mulbarton Wanderers", "status": "FT", "decision": "",
                  "round": "Second Round Qualifying Replay", "date": "2026-09-29"}
        before = copy.deepcopy(source)
        summary, candidate = stage.stage(source, {
            "production_mutation": False, "blocked": [], "replay_candidates": [replay]})
        self.assertEqual(source, before)
        self.assertEqual(summary["staged_count"], 1)
        self.assertEqual(summary["staged"][0]["next_fixture"], "Mulbarton Wanderers v Gloucester City")
        self.assertEqual(candidate["results"]["Mulbarton Wanderers"]["winner"], "Mulbarton Wanderers")

    def test_unlisted_decided_result_cannot_be_treated_as_replay_original(self):
        source = data()
        source["result_history"] = {"Other": [{
            "home": "Other", "away": "Opponent",
            "home_score": 1, "away_score": 0, "winner": "Other",
            "status": "FT", "decision": "",
            "round": "Second Round Qualifying", "date": "2026-09-19"}]}
        source["fixtures"] = {"Other": {
            "home": "Other", "away": "Next Club",
            "date": "2026-10-03", "round": "Third Round Qualifying"}}
        replay = {"home": "Opponent", "away": "Other",
                  "home_score": 0, "away_score": 2, "winner": "Other",
                  "status": "FT", "decision": "",
                  "round": "Second Round Qualifying Replay", "date": "2026-09-29"}
        with self.assertRaisesRegex(ValueError, "replay original not uniquely verified"):
            stage.stage(source, {"production_mutation": False, "blocked": [], "replay_candidates": [replay]})


if __name__ == "__main__":
    unittest.main()
