"""Protect the read-only League & Tier review boundary."""
import csv
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from updater.league_tier_readonly import (
    EFL_SOURCE, MATCH_STATUSES, PREMIER_LEAGUE_SOURCE, SOURCE, STEPS_5_6_SOURCE,
    build_audit, key, load_allocations, match_population, write_audit,
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

    def test_steps_5_to_6_tables_include_conditional_places_and_exclude_appendix(self):
        official, provisional, counts = load_allocations([STEPS_5_6_SOURCE])
        self.assertEqual(counts, {"official_initial_allocation": 655, "provisional_ambiguous": 5})
        self.assertEqual(
            {row["club"] for row in provisional},
            {"AFC Knowsley", "Halewood Apollo", "Crewe", "Harlow Town", "Guernsey or Peacehaven & Telscombe"},
        )
        self.assertEqual(official[key("Amersham Town")][0]["fa_step"], 5)
        self.assertEqual(official[key("Holmer Green")][0]["fa_step"], 6)
        self.assertNotIn(key("Copthorne"), official)

    def test_real_roster_complete_without_publication_or_awards(self):
        rows, meta = build_audit()
        self.assertEqual(meta["season"], "2026-27")
        self.assertEqual(meta["original_clubfinder_clubs"], 651)
        self.assertEqual(meta["initial_fa_rows_by_step"], {
            "1": 24, "2": 48, "3": 88, "4": 176, "5": 320, "6": 340
        })
        self.assertGreaterEqual(meta["total_distinct_clubs"], 651)
        self.assertTrue(meta["read_only"])
        self.assertFalse(meta["public_promotion"])
        self.assertFalse(meta["giant_killer_awards_enabled"])
        self.assertTrue(all(not row["approved_tier"] for row in rows))
        names = {row["club"]: row for row in rows}
        self.assertEqual(names["Crowborough Athletic FC"]["proposed_tier"], 8)
        self.assertEqual(names["Amersham Town FC"]["proposed_tier"], 9)
        self.assertEqual(names["Harlow Town FC"]["match_status"], "provisional_ambiguous")
        self.assertEqual(names["Harlow Town FC"]["proposed_tier"], "")
        self.assertEqual(names["Westfield FC"]["match_status"], "ambiguous_source")
        self.assertIn("Step 4", names["Westfield FC"]["suggestions"])
        self.assertIn("Step 6", names["Westfield FC"]["suggestions"])
        self.assertIn(names["Crowborough Athletic FC"]["match_status"],
                      ("matched_exact_initial", "matched_normalized_initial"))
        self.assertTrue(any(row["match_status"] == "missing_allocation" for row in rows))
        self.assertEqual(sum(meta["original_match_status"].values()), 651)

    def test_official_membership_has_92_distinct_clubs_and_explicit_tiers(self):
        official, provisional, counts = load_allocations([PREMIER_LEAGUE_SOURCE, EFL_SOURCE])
        self.assertEqual(counts, {"official_season_membership": 92})
        self.assertEqual(len(official), 92)
        self.assertFalse(provisional)
        memberships = [row for club_rows in official.values() for row in club_rows]
        self.assertEqual(Counter(row["tier"] for row in memberships), {1: 20, 2: 24, 3: 24, 4: 24})
        self.assertTrue(all(row["fa_step"] is None and row["season"] == "2026-27" for row in memberships))
        for name, tier in [
            ("Ipswich Town", 1), ("Wolverhampton Wanderers", 2), ("Leyton Orient", 3), ("Rochdale", 4)
        ]:
            with self.subTest(club=name):
                self.assertEqual(official[key(name)][0]["tier"], tier)

    def test_both_populations_and_review_queue_use_membership(self):
        rows, meta = build_audit()
        journey = [row for row in rows if row["population"] == "companion-journey-registry"]
        self.assertEqual(meta["season_membership_source_rows"], 92)
        self.assertEqual(len(journey), 92)
        self.assertEqual(Counter(row["proposed_tier"] for row in journey), {1: 20, 2: 24, 3: 24, 4: 24})
        self.assertTrue(all(row["source_fa_step"] == "" and row["approved_tier"] == "" for row in journey))
        self.assertTrue(all(row["source_status"] == "official_season_membership" for row in journey))
        self.assertEqual(sum(meta["companion_match_status"].values()), 92)
        self.assertEqual(sum(meta["original_match_status"].get(status, 0) for status in MATCH_STATUSES), 626)
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            write_audit(rows, meta, folder)
            with (folder / "league-tier-review-queue-2026-27.csv").open() as file:
                waiting = list(csv.DictReader(file))
        self.assertEqual(Counter(row["match_status"] for row in waiting), {
            "missing_allocation": 18, "ambiguous_source": 4, "provisional_ambiguous": 3
        })
        self.assertTrue(all(row["population"] == "original-clubfinder" for row in waiting))

    def test_only_safe_suffix_normalisation_and_no_afc_prefix_collision(self):
        self.assertEqual(key("Crowborough Athletic FC"), key("Crowborough Athletic"))
        self.assertNotEqual(key("AFC Liverpool"), key("Liverpool FC"))
        self.assertNotEqual(key("AFC Wimbledon"), key("Wimbledon FC"))
        self.assertNotEqual(key("Biggleswade Town"), key("Biggleswade"))

    def test_provisional_alternative_does_not_assign_a_tier(self):
        _, pending, _ = load_allocations([SOURCE, STEPS_5_6_SOURCE])
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

    def test_conflicting_membership_and_nls_evidence_stay_ambiguous(self):
        nls, _, _ = load_allocations([SOURCE])
        league, _, _ = load_allocations([EFL_SOURCE])
        membership = league[key("Rochdale")][0]
        allocation = dict(nls[key("AFC Fylde")][0], club="Rochdale")
        result, = match_population(
            [{"club": "Rochdale AFC"}], {key("Rochdale"): [membership, allocation]}, []
        )
        self.assertEqual(result["match_status"], "ambiguous_source")
        self.assertEqual(result["proposed_tier"], "")
        self.assertIn("Tier 4", result["suggestions"])
        self.assertIn("Step 1", result["suggestions"])

    def test_invalid_professional_evidence_fails_closed(self):
        base = dict(season="2026-27", fa_step="", tier=3, club="Example FC", league="Test",
                    division="Test", source_url="https://www.efl.com", source_as_of="2026-11-21",
                    source_status="official_season_membership")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "membership.csv"
            for invalid in (dict(tier=""), dict(tier=5), dict(fa_step=1), dict(season="2025-26")):
                with self.subTest(invalid=invalid):
                    with path.open("w", newline="") as file:
                        writer = csv.DictWriter(file, fieldnames=base.keys())
                        writer.writeheader()
                        writer.writerow(base | invalid)
                    with self.assertRaisesRegex(ValueError, "Invalid season membership"):
                        load_allocations([path])

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
