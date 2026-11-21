#!/usr/bin/env python3
"""Construction Law regressions for the read-only, round-aware Club Entry Radar."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from updater.club_entry_radar import inspect_rounds, analyze, round_fixtures


def html(records):
    return ("const GROUNDS=" + json.dumps(records) + ";"
            "const LAW2_ORIGIN_LOCATIONS=[];")


def club(name, ground, postcode, verification="unverified"):
    return {"name": name, "ground": ground, "postcode": postcode,
            "verification": verification}


class ClubEntryRadarTests(unittest.TestCase):
    def setUp(self):
        self.comp = {"season": "2026-27", "updated_at": "test",
                     "fixtures": {"a": {
                         "round": "Second Round Proper",
                         "home": "Port Vale", "away": "Leyton Orient",
                         "venue": {"ground": "Vale Park", "postcode": "ST6 1AW"},
                     }}}
        self.production = html([club("Port Vale FC", "Vale Park", "ST6 1AW", "verified")])
        self.beta = html([club("Port Vale FC", "Vale Park", "ST6 1AW", "verified"),
                          club("Leyton Orient FC", "BetWright Stadium", "E10 5NF")])

    def test_new_entrant_is_flagged_in_production_not_beta(self):
        report = inspect_rounds(self.comp, {"production": self.production, "beta": self.beta})
        current = report["rounds"][0]
        self.assertEqual(current["entrant_count"], 2)
        self.assertEqual(current["coverage"]["production"]["missing_ground"], 1)
        self.assertEqual(current["coverage"]["beta"]["ground_recorded_coordinates_pending"], 1)
        orient = next(c for c in current["clubs"] if c["club"] == "Leyton Orient")
        self.assertNotIn("venue", orient)
        self.assertEqual(orient["sources"]["beta"]["postcode"], "E10 5NF")
        self.assertTrue(report["read_only"])
        self.assertFalse(report["automatic_ground_promotion"])

    def test_rounds_are_derived_not_locked_to_second_proper_or_40(self):
        self.comp["round_fixtures"] = {"Third Round Proper": [
            {"home": "Leyton Orient", "away": "Newcastle United"},
            {"home": "Other Team", "away": "Third Team"}]}
        report = inspect_rounds(self.comp, {"beta": self.beta})
        self.assertEqual([r["entrant_count"] for r in report["rounds"]], [2, 4])
        later = report["rounds"][1]
        self.assertEqual(later["new_to_observed_rounds"], 3)
        self.assertEqual(later["coverage"]["beta"]["missing_ground"], 3)

    def test_replays_follow_parent_round_before_later_entry_counts(self):
        comp = {"season": "2026-27",
                "fixtures": {
                    "a": {"round": "Preliminary Round", "home": "A", "away": "B"},
                    "b": {"round": "First Round Proper", "home": "C", "away": "D"}},
                "replays": {
                    "r": {"round": "Preliminary Round Replay", "home": "A", "away": "B"}}}
        report = inspect_rounds(comp, {"beta": html([])})
        self.assertEqual([x["round"] for x in report["rounds"]],
                         ["Preliminary Round", "Preliminary Round Replay", "First Round Proper"])
        self.assertEqual([x["new_to_observed_rounds"] for x in report["rounds"]],
                         [2, 0, 2])

    def test_afc_liverpool_must_not_borrow_liverpool_ground(self):
        self.comp["fixtures"]["a"]["home"] = "AFC Liverpool"
        self.comp["fixtures"]["a"]["away"] = "Liverpool FC"
        report = inspect_rounds(self.comp, {"beta": html([
            club("Liverpool FC", "Anfield", "L4 0TH")])})
        self.assertEqual(report["rounds"][0]["coverage"]["beta"]["identity_conflict"], 1)
        self.assertEqual(report["rounds"][0]["coverage"]["beta"]["ground_recorded_coordinates_pending"], 1)

    def test_away_fixture_ground_is_not_entrant_home_ground(self):
        report = inspect_rounds(self.comp, {"beta": html([])})
        self.assertEqual(report["rounds"][0]["coverage"]["beta"]["missing_ground"], 2)
        self.assertNotIn("Vale Park", json.dumps(report))

    def test_duplicate_and_ambiguous_records_fail_closed(self):
        h = html([club("Leyton Orient", "One", "E10 5NF"),
                  club("Leyton Orient FC", "Two", "E10 5NF")])
        report = inspect_rounds(self.comp, {"beta": h})
        self.assertEqual(report["rounds"][0]["coverage"]["beta"]["identity_conflict"], 1)

    def test_reingestion_is_idempotent_and_original_objects_untouched(self):
        before = json.dumps(self.comp, sort_keys=True)
        first = inspect_rounds(self.comp, {"beta": self.beta})
        second = inspect_rounds(self.comp, {"beta": self.beta})
        self.assertEqual(first, second)
        self.assertEqual(before, json.dumps(self.comp, sort_keys=True))

    def test_disagreeing_bucket_and_tie_rounds_fail_closed(self):
        self.comp["round_fixtures"] = {"Third Round Proper": [
            {"round": "Second Round Proper", "home": "A", "away": "B"}]}
        with self.assertRaisesRegex(ValueError, "Conflicting round"):
            round_fixtures(self.comp)

    def test_season_disagreement_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "season mismatch"):
            inspect_rounds(self.comp, {"beta": self.beta},
                           {"season": "2025-26", "clubs": []})

    def test_analysis_never_changes_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "beta").mkdir()
            (root / "competition.json").write_text(json.dumps(self.comp))
            (root / "journey-club-registry.json").write_text(
                json.dumps({"season": "2026-27", "clubs": []}))
            (root / "clubfinder.html").write_text(self.production)
            (root / "beta/clubfinder-beta.html").write_text(self.beta)
            before = {p.relative_to(root).as_posix(): p.read_bytes()
                      for p in root.rglob("*") if p.is_file()}
            self.assertEqual(analyze(root)["rounds"][0]["entrant_count"], 2)
            after = {p.relative_to(root).as_posix(): p.read_bytes()
                     for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
