#!/usr/bin/env python3
"""Safety regressions for the read-only new-entrant custodian audit."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from updater.audit_active_custodian_locations import (
    analyze, competition_participants, display_key, identity_key,
    next_round_entrants,
)


class CustodianLocationAuditTests(unittest.TestCase):
    def test_leading_afc_is_significant_to_identity(self):
        self.assertNotEqual(identity_key("Liverpool FC"), identity_key("AFC Liverpool"))
        self.assertNotEqual(identity_key("AFC Bournemouth"), identity_key("Bournemouth FC"))
        # The existing UI lookup normaliser is looser: flag it, do not promote.
        self.assertEqual(display_key("Liverpool FC"), display_key("AFC Liverpool"))

    def test_historical_result_proves_club_has_entered(self):
        fixture = {
            "home": "Leyton Orient",
            "away": "Harborough Town",
            "round": "First Round Proper",
        }
        data = {
            "results": {"Leyton Orient": fixture},
            "fixtures": {},
            "round_fixtures": {},
        }
        self.assertIn(identity_key("Leyton Orient FC"), competition_participants(data))

    def test_next_draw_comes_from_fixtures_not_old_results(self):
        data = {
            "results": {"Leyton Orient": {"home": "Leyton Orient", "away": "Harborough Town"}},
            "fixtures": {
                "Leyton Orient": {
                    "round": "Second Round Proper",
                    "home": "Port Vale",
                    "away": "Leyton Orient",
                    "venue": {"ground": "Vale Park", "postcode": "ST6 1AW"},
                }
            },
        }
        entries = next_round_entrants(data)
        self.assertEqual(set(entries), {"port vale", "leyton orient"})
        self.assertNotIn("Harborough Town", entries.values())
        self.assertTrue(all(isinstance(name, str) for name in entries.values()))

    def test_fchd_only_candidate_is_not_promoted_or_marked_verified(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            comp = {
                "season": "2026-27",
                "updated_at": "2026-11-21T00:00:00Z",
                "fixtures": {
                    "Leyton Orient": {
                        "round": "Second Round Proper",
                        "home": "Port Vale",
                        "away": "Leyton Orient",
                        "venue": {"ground": "Vale Park", "postcode": "ST6 1AW"},
                    }
                },
                "results": {
                    "Leyton Orient": {
                        "round": "First Round Proper",
                        "home": "Leyton Orient",
                        "away": "Harborough Town",
                        "venue": {"ground": "Gaughan Group Stadium", "postcode": "E10 5NF"},
                    }
                },
            }
            registry_clubs = [
                {"club": "Leyton Orient FC", "entry_round": "First Round Proper",
                 "registry_state": "awaiting-journey-entry",
                 "supporting_ground_evidence": [{
                     "type": "fchd-gazetteer-candidate",
                     "ground": "Gaughan Group Stadium", "postcode": "E10 5NF",
                 }]}
            ]
            registry_clubs += [
                {"club": f"Other Entrant {n}", "entry_round": "Third Round Proper",
                 "registry_state": "awaiting-journey-entry",
                 "supporting_ground_evidence": []}
                for n in range(251)
            ]
            reg = {"season": "2026-27", "clubs": registry_clubs}
            (root / "competition.json").write_text(json.dumps(comp))
            (root / "journey-club-registry.json").write_text(json.dumps(reg))
            (root / "beta").mkdir()
            html = (
                "const ELIGIBLE=" + json.dumps([{"name": f"Origin {n}"} for n in range(651)]) + ";"
                "let GROUNDS=" + json.dumps([{
                    "name": "Port Vale FC", "ground": "Vale Park",
                    "postcode": "ST6 1AW", "verification": "verified"
                }]) + ";"
                "const LAW2_ORIGIN_LOCATIONS=[];"
            )
            (root / "clubfinder.html").write_text(html)
            (root / "beta" / "clubfinder-beta.html").write_text(html)
            before = {str(p.relative_to(root)): p.read_bytes()
                      for p in root.rglob("*") if p.is_file()}
            output = analyze(root)
            self.assertEqual(output["second_round_clubs"], 2)
            for build in ("production", "beta"):
                missing = output["missing_second_round_custodian_locations"][build]
                self.assertEqual(len(missing), 1)
                self.assertEqual(missing[0]["club"], "Leyton Orient FC")
                self.assertEqual(missing[0]["candidate_postcode"], "E10 5NF")
            self.assertEqual(output["registry_marked_awaiting_but_seen"], 1)
            self.assertFalse(output["automatic_ground_promotion"])
            after = {str(p.relative_to(root)): p.read_bytes()
                     for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
