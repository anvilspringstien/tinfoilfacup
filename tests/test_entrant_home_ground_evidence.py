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
            self.assertIn(row["official_home_ground_source"].split("/")[2], ("www.leytonorient.com", "www.port-vale.co.uk", "www.afcwimbledon.co.uk", "barnetfc.com", "www.lutontown.co.uk", "www.stockportcounty.com", "www.accringtonstanley.co.uk", "www.bristolrovers.co.uk", "www.cambridgeunited.com", "chesterfield-fc.co.uk", "www.crewealex.net", "www.exetercityfc.co.uk", "www.doncasterroversfc.co.uk", "www.readingfc.co.uk", "www.shrewsburytown.com", "www.swindontownfc.co.uk", "www.gillinghamfootballclub.com", "www.barnsleyfc.co.uk", "shop.blackpoolfc.co.uk", "www.bradfordcityafc.com", "www.burtonalbionfc.co.uk", "www.ctfc.com", "tickets.colchesterunited.net", "www.lcfc.com", "www.mansfieldtown.net", "shop.nottscountyfc.co.uk", "www.oldhamathletic.co.uk", "shop.wwfc.com", "www.yorkcityfootballclub.co.uk"))
            self.assertEqual(row["source_review"], "official-ground-and-postcode-confirmed")
            if row["coordinates"] is None:
                self.assertEqual(row["coordinates_review"], "pending")
                self.assertEqual(row["review_status"], "awaiting-coordinates-and-human-promotion")
            else:
                self.assertEqual(row["official_identity"], "AFC Wimbledon")
                self.assertEqual(row["coordinates_review"], "published-by-club-matchday-guide")
                self.assertEqual(row["review_status"], "awaiting-human-promotion")
    def test_gillingham_stadium_postcode_resolved_without_promotion(self):
        doc = json.loads((ROOT / "updater" / "entrant-home-ground-evidence-2026.json").read_text(encoding="utf-8"))
        by_id = {x["official_identity"]: x for x in doc["clubs"]}
        gills = by_id["Gillingham FC"]
        self.assertEqual(gills["postcode"], "ME7 2PE")
        self.assertEqual(gills["ground"], "MEMS Priestfield Stadium")
        self.assertIsNone(gills["coordinates"])
        self.assertEqual(gills["review_status"], "awaiting-coordinates-and-human-promotion")
        resolved = [x for x in doc.get("resolved_conflicts", []) if x["official_identity"] == "Gillingham FC"]
        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0]["stadium_postcode"], "ME7 2PE")
        self.assertEqual(resolved[0]["other_postcode"], "ME7 4DD")
        self.assertEqual(resolved[0]["status"], "resolved-stadium-postcode-only")
        self.assertFalse(any(x["official_identity"] == "Gillingham FC" for x in doc.get("unresolved_conflicts", [])))

    def test_tie_venue_not_away_club_home_ground(self):
        doc = json.loads((ROOT / "updater" / "entrant-home-ground-evidence-2026.json").read_text(encoding="utf-8"))
        by_id = {r["official_identity"]: r for r in doc["clubs"]}
        self.assertEqual(by_id["Leyton Orient FC"]["postcode"], "E10 5NF")
        self.assertEqual(by_id["Port Vale FC"]["postcode"], "ST6 1AW")
        self.assertNotEqual(by_id["Leyton Orient FC"]["ground"], by_id["Port Vale FC"]["ground"])

if __name__ == "__main__":
    unittest.main()
