"""Protect the read-only League & Tier review boundary."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from updater.league_tier_readonly import (
    ROOT, SOURCE, key, load_allocations, match_population, build_audit, write_audit
)


class LeagueTierReadOnlyTests(unittest.TestCase):
    def test_initial_fa_document_is_season_scoped_and_complete_for_steps_1_to_4(self):
        official, provisional, counts = load_allocations([SOURCE])
        self.assertEqual(counts, {"official_initial_allocation": 335, "provisional_ambiguous": 1})
        self.assertEqual(sum(len(v) for v in official.values()), 335)
        self.assertEqual(len(provisional), 1)
        self.assertIn("Guernsey or Peacehaven & Telscombe", provisional[0]["club"])
        self.assertEqual(official[key("Crowborough Athletic")][0]["fa_step"], 4)
        self.assertEqual(official[key("AFC Fylde")][0]["fa_step"], 1)
        for club_rows in official.values():
            for r in club_rows:
                self.assertEqual(r["source_as_of"], "2026-05-14")
                self.assertNotIn("verified", r["source_status"])

    def test_real_roster_complete_without_publication_or_awards(self):
        rows, meta = build_audit()
        self.assertEqual(meta["season"], "2026-27")
        self.assertEqual(meta["original_clubfinder_clubs"], 651)
        self.assertGreaterEqual(meta["total_distinct_clubs"], 651)
        self.assertTrue(meta["read_only"])
        self.assertFalse(meta["public_promotion"])
        self.assertFalse(meta["giant_killer_awards_enabled"])
        self.assertTrue(all(not row["approved_tier"] for row in rows))
        names = {row["club"]: row for row in rows}
        self.assertEqual(names["Crowborough Athletic FC"]["proposed_tier"], 8)
        self.assertIn(names["Crowborough Athletic FC"]["match_status"],
                      ("matched_exact_initial", "matched_normalized_initial"))
        self.assertTrue(any(row["match_status"] == "missing_allocation" for row in rows))
        self.assertEqual(sum(meta["original_match_status"].values()), 651)

    def test_only_safe_suffix_normalisation_and_no_afc_prefix_collision(self):
        self.assertEqual(key("Crowborough Athletic FC"), key("Crowborough Athletic"))
        self.assertNotEqual(key("AFC Liverpool"), key("Liverpool FC"))
        self.assertNotEqual(key("AFC Wimbledon"), key("Wimbledon FC"))
        self.assertNotEqual(key("Biggleswade Town"), key("Biggleswade"))

    def test_provisional_alternative_does_not_assign_a_tier(self):
        _, pending, _ = load_allocations([SOURCE])
        rows = match_population([
            {"club": "Peacehaven & Telscombe FC", "population": "test"},
            {"club": "Guernsey FC", "population": "test"},
        ], {}, pending)
        self.assertTrue(all(row["match_status"] == "provisional_ambiguous" for row in rows))
        self.assertTrue(all(row["proposed_tier"] == "" and row["approved_tier"] == "" for row in rows))

    def test_duplicate_identity_blocks_automatic_classification(self):
        first = dict(club="Some Town", fa_step=2, league="National League",
                     division="North", source_status="official_initial_allocation",
                     source_as_of="2026-05-14", source_url="https://www.thefa.com")
        second = dict(first, fa_step=3, division="South")
        rows = match_population([{"club": "Some Town FC", "population": "test"}],
                                {key("Some Town"): [first, second]}, [])
        self.assertEqual(rows[0]["match_status"], "ambiguous_source")
        self.assertEqual(rows[0]["proposed_tier"], "")

    def test_unsupported_step_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "invalid.csv"
            with p.open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=[
                    "fa_step", "club", "league", "division", "source_url",
                    "source_as_of", "source_status"
                ])
                w.writeheader()
                w.writerow(dict(fa_step=7, club="Fake FC", league="Test", division="Test",
                                source_url="https://thefa.com", source_as_of="2026-05-14",
                                source_status="official_initial_allocation"))
            with self.assertRaisesRegex(ValueError, "Invalid source allocation"):
                load_allocations([p])

    def test_diagnostics_write_only_to_requested_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "results"
            rows = [dict.fromkeys((
                "club", "population", "entry_round", "postcode", "match_status",
                "source_club", "source_fa_step", "proposed_tier", "approved_tier",
                "league", "division", "source_as_of", "source_url", "source_status",
                "review_note", "suggestions"
            ), "")]
            rows[0].update(club="Some Club", population="original-clubfinder",
                           match_status="missing_allocation")
            meta = {"original_clubfinder_clubs": 1, "companion_only_clubs": 0,
                    "original_match_status": {"missing_allocation": 1}}
            write_audit(rows, meta, folder)
            self.assertEqual(len(list(folder.iterdir())), 4)
            self.assertIn("Some Club", (folder / "league-tier-review-queue-2026-27.csv").read_text())
            self.assertIn("NOT APPROVED", (folder / "league-tier-audit-2026-27.md").read_text())


if __name__ == "__main__":
    unittest.main()
