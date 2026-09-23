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


if __name__ == "__main__":
    unittest.main()
