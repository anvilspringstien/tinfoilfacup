"""Regress the Club Audit contract without changing or publishing source data."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from updater.audit_active_custodian_locations import analyze as custody_audit
from updater.club_audit import (
    APPROVALS, ROOT, build_report, identity_index, league_fields, location_fields, location_index, round_history,
)
from updater.league_tier_approval import active_events, digest
from updater.league_tier_readonly import load_population

SAMPLE = ROOT / "docs/examples/club-audit-2026-11-25.json"
GENERATION_DAY = date(2026, 11, 25)


class ClubAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report(ROOT, GENERATION_DAY)
        cls.sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
        cls.snapshot = {row["club"]: row for row in cls.sample["clubs"]}

    def test_current_population_reconciles_with_active_approval_events(self):
        population, original = load_population()
        roster = {row["club"]: row for row in population}
        records = self.report["clubs"]
        self.assertEqual(len(records), len(roster))
        self.assertEqual(len({row["club_id"] for row in records}), len(records))
        self.assertEqual(set(roster), {row["club"] for row in records})
        self.assertEqual(self.report["summary"]["original_clubfinder_identities"], original)
        ledger = json.loads((ROOT / APPROVALS).read_text(encoding="utf-8"))
        decisions = {event["club_id"]: event for event in active_events(ledger["events"]).values()
                     if event["scope"] == "season"}
        for row in records:
            club = row["club"]
            expected = digest({"club": club, "population": roster[club]["population"], "season": row["season"]})
            self.assertEqual(row["club_id"], expected)
            self.assertEqual(row["league_tier"]["status"],
                             {"approve": "approved", "hold": "held"}[decisions[expected]["action"]]
                             if expected in decisions else "missing")
        self.assertEqual(self.sample["summary"]["identities"], 743)
        self.assertEqual(self.sample["summary"]["season_memberships"], {"approved": 740, "held": 3})

    def test_coverage_matches_canonical_website_and_custody_audits(self):
        audit = self.report["summary"]
        website = audit["canonical_website_queue"]
        self.assertEqual(audit["eligible_website_coverage"]["beta"],
                         {"eligible": website["eligible"], "linked": website["eligible_linked"]})
        custody = custody_audit(ROOT)
        self.assertEqual(audit["ground_record_gaps"]["second_round_proper"]["missing"],
                         {build: len(custody["missing_second_round_custodian_locations"][source])
                          for build, source in (("public", "production"), ("beta", "beta"))})
        self.assertEqual(self.sample["summary"]["eligible_website_coverage"]["beta"],
                         {"eligible": 651, "linked": 334})
        self.assertEqual(self.sample["summary"]["ground_record_gaps"]["second_round_proper"]["missing"],
                         {"public": 31, "beta": 0})

    def test_club_confirmations_remain_field_and_build_specific(self):
        glebe = self.snapshot["Chislehurst Glebe FC"]["published"]
        self.assertEqual(glebe["public"]["postcode"]["value"], "BR7 6HA")
        self.assertEqual(glebe["beta"]["postcode"]["value"], "BR7 6SD")
        self.assertEqual(glebe["beta"]["postcode"]["review_status"], "club_confirmed")
        self.assertNotEqual(glebe["beta"]["ground"]["review_status"], "club_confirmed")
        self.assertEqual(glebe["public"]["coordinates"]["value"], glebe["beta"]["coordinates"]["value"])

        billingshurst = self.snapshot["Billingshurst FC"]["published"]
        self.assertEqual(billingshurst["beta"]["ground"]["value"], "Four Seasons Fuel Stadium")
        self.assertNotEqual(billingshurst["beta"]["postcode"]["review_status"], "club_confirmed")
        for row in billingshurst.values():
            self.assertEqual(row["postcode"]["value"], "RH14 9HZ")

        regent = self.snapshot["Brightlingsea Regent FC"]["published"]
        for row in regent.values():
            self.assertEqual(row["ground"]["value"], "North Road")
            self.assertEqual(row["postcode"]["value"], "CO7 0PL")
            self.assertEqual(row["ground"]["review_status"], "club_confirmed")
        for row in (glebe, billingshurst, regent):
            self.assertEqual(row["beta"]["website"]["review_status"], "verified")
            self.assertEqual(row["public"]["website"]["review_status"], "verified_unmapped")
            self.assertIsNone(row["public"]["website"]["value"])

    def test_entrant_evidence_does_not_fill_public_gaps_or_invent_coordinates(self):
        row = self.snapshot["Leyton Orient FC"]
        self.assertEqual(row["membership"]["population"], "companion-journey-registry")
        self.assertIn("Second Round Proper", {r["round"] for r in row["competition"]["observed_rounds"]})
        self.assertEqual(row["published"]["public"]["record_status"], "missing")
        self.assertIsNone(row["published"]["public"]["postcode"]["value"])
        beta = row["published"]["beta"]
        self.assertEqual(beta["ground"]["value"], "BetWright Stadium")
        self.assertEqual(beta["postcode"]["value"], "E10 5NF")
        self.assertEqual(beta["postcode"]["review_status"], "official_source_confirmed")
        self.assertEqual(beta["coordinates"]["review_status"], "pending")
        self.assertIsNone(beta["coordinates"]["value"])
        self.assertEqual(row["league_tier"]["tier"], 3)
        self.assertEqual(row["tie_day"]["status"], "not_approved")

    def test_location_and_league_holds_remain_visible(self):
        for club, existing, questioned in (
            ("Ossett United FC", "WF5 9HA", "WF5 9HL"),
            ("Peacehaven & Telscombe FC", "BN10 8RJ", "BN10 8WS"),
        ):
            row = self.snapshot[club]
            for build in ("public", "beta"):
                self.assertEqual(row["published"][build]["postcode"]["value"], existing)
            self.assertTrue(any(item["field"] == "postcode" and item.get("observed_value") == questioned
                                for item in row["discrepancies"]))
        for club in ("Boro Rangers FC", "Cribbs FC", "Holmesdale FC"):
            row = self.snapshot[club]
            self.assertEqual(row["league_tier"]["status"], "held")
            self.assertIsNone(row["league_tier"]["tier"])
            self.assertTrue(row["league_tier"]["decision"]["reason"])
            self.assertEqual(row["tie_day"]["interval_decisions"], [])
        self.assertFalse(self.snapshot["Holmesdale FC"]["membership"]["eligible_in"]["beta"])
        self.assertIn("Petts Wood & Holmesdale", self.sample["reconciliation"]["unmatched_played_labels"])

    def test_no_fuzzy_identity_join_or_shared_location_merge(self):
        population = [{"club": club} for club in ("Liverpool FC", "AFC Liverpool", "Future Athletic FC")]
        index = identity_index(population)
        self.assertEqual(len(index), 3)
        rounds = {"rounds": [{"round": "Unfamiliar Round", "clubs": [
            {"identity": "future athletic", "club": "Future Athletic"},
            {"identity": "future athletic town", "club": "Future Athletic Town"},
            {"identity": "petts wood and holmesdale", "club": "Petts Wood & Holmesdale"},
        ]}]}
        history, unresolved = round_history(rounds, population, [])
        self.assertEqual([x["round"] for x in history["Future Athletic FC"]], ["Unfamiliar Round"])
        self.assertEqual({x["label"] for x in unresolved}, {"Future Athletic Town", "Petts Wood & Holmesdale"})
        html = ('const GROUNDS=[{"name":"Liverpool FC","postcode":"L4 0TH"},'
                '{"name":"Future Athletic FC","postcode":"L4 0TH","lat":0,"lon":0}];'
                'const LAW2_ORIGIN_LOCATIONS=[];')
        index = location_index(html)
        empty = {"ground": [], "postcode": [], "coordinates": []}
        self.assertEqual(location_fields("AFC Liverpool", "example", index, empty)["record_status"], "ambiguous")
        self.assertEqual(location_fields("Future Athletic FC", "example", index, empty)["coordinates"]["value"],
                         {"lat": 0, "lon": 0})
        with self.assertRaisesRegex(ValueError, "Ambiguous registry identity"):
            identity_index([{"club": "Future Athletic FC"}, {"club": "Future Athletic"}])

    def test_tie_day_needs_an_independent_dated_decision(self):
        entry = {"membership_evidence": {}, "league": "Example", "division": "Premier", "proposed_tier": 7}
        season = {"scope": "season", "action": "approve", "event_id": "a", "reviewed_at": "2026-11-25",
                  "entry": entry, "reason": "Reviewed season"}
        dates = {date(2026, 9, 1), date(2026, 9, 8)}
        _, tie_day = league_fields([season], dates, (), ())
        self.assertEqual([r["status"] for r in tie_day["played_dates"]], ["not_approved"] * 2)
        interval = {"scope": "interval", "action": "approve", "event_id": "b",
                    "valid_from": "2026-09-01", "valid_until": "2026-09-08", "interval_sha256": "c",
                    "entry": {"interval_evidence": [{"sha256": "c"}]}, "reason": "Reviewed interval"}
        _, tie_day = league_fields([season, interval], dates, (), ())
        self.assertEqual([r["status"] for r in tie_day["played_dates"]], ["approved", "not_approved"])

    def test_deterministic_cli_and_checkout_remains_unmodified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path, expected in self.report["source_revisions"].items():
                source = ROOT / path
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), expected)
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)

            def tree_hashes():
                return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in root.rglob("*") if p.is_file()}

            before = tree_hashes()
            command = [sys.executable, "-B", "-m", "updater.club_audit", "--generated-on", "2026-11-25"]
            first = subprocess.check_output(command, cwd=root)
            self.assertEqual(first, subprocess.check_output(command, cwd=root))
            self.assertEqual(json.loads(first), self.report)
            self.assertEqual(tree_hashes(), before)
            if before == self.sample["source_revisions"]:
                args = [arg for club in self.snapshot for arg in ("--club", club)]
                self.assertEqual(subprocess.check_output(command + args, cwd=root), SAMPLE.read_bytes())


if __name__ == "__main__":
    unittest.main()
