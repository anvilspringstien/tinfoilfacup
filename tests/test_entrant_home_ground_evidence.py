#!/usr/bin/env python3
"""Construction Law: evidence is never equivalent to promoted location."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class EntrantGroundEvidenceTests(unittest.TestCase):
    def test_evidence_is_non_promoting_and_reviewable(self):
        doc = json.loads((ROOT / "updater" / "entrant-home-ground-evidence-2026.json").read_text(encoding="utf-8"))
        self.assertEqual(doc["season"], "2026-27")
        self.assertFalse(doc["safety"]["automated_ground_promotion"])
        self.assertFalse(doc["safety"]["verified_location_badge_authorized"])
        self.assertTrue(doc["safety"]["coordinates_required_before_location_promotion"])
        ids = [r["official_identity"] for r in doc["clubs"]]
        self.assertEqual(len(ids), len(set(ids)))
        for row in doc["clubs"]:
            self.assertIn(row["official_home_ground_source"].split("/")[2], ("www.leytonorient.com", "www.port-vale.co.uk"))
            self.assertEqual(row["source_review"], "official-ground-and-postcode-confirmed")
            self.assertIsNone(row["coordinates"])
            self.assertEqual(row["review_status"], "awaiting-coordinates-and-human-promotion")
    def test_tie_venue_not_away_club_home_ground(self):
        doc = json.loads((ROOT / "updater" / "entrant-home-ground-evidence-2026.json").read_text(encoding="utf-8"))
        by_id = {r["official_identity"]: r for r in doc["clubs"]}
        self.assertEqual(by_id["Leyton Orient FC"]["postcode"], "E10 5NF")
        self.assertEqual(by_id["Port Vale FC"]["postcode"], "ST6 1AW")
        self.assertNotEqual(by_id["Leyton Orient FC"]["ground"], by_id["Port Vale FC"]["ground"])

if __name__ == "__main__":
    unittest.main()
