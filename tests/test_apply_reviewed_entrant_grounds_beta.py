import json
import unittest
from pathlib import Path
from updater.apply_reviewed_entrant_grounds_beta import transform,ROOT
from updater.audit_active_custodian_locations import array_from_html,identity_key

class GuardedEntrantGroundPublishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(ROOT/"beta/clubfinder-beta.html").read_text("utf-8")
        cls.evidence=json.loads((ROOT/"updater/entrant-home-ground-evidence-2026.json").read_text("utf-8"))
        cls.competition=json.loads((ROOT/"competition.json").read_text("utf-8"))

    def test_idempotent_source_review_and_unverified_location_only(self):
        updated,report=transform(self.source,self.evidence,self.competition)
        self.assertEqual(report["new_pending"]+report["already_pending"],31)
        self.assertEqual(report["other_existing"],9)
        self.assertFalse(report["automatic_verified"])
        self.assertFalse(report["mileage_changed"])
        original=array_from_html(self.source,"GROUNDS")
        records=array_from_html(updated,"GROUNDS")
        self.assertEqual(records[:len(original)],original,"Original locations must not be rewritten")
        self.assertEqual(array_from_html(self.source,"LAW2_ORIGIN_LOCATIONS"),
                         array_from_html(updated,"LAW2_ORIGIN_LOCATIONS"))
        by_id={identity_key(row["name"]):row for row in records if row.get("preview_evidence_only")}
        self.assertEqual(len(by_id),31)
        for row in by_id.values():
            self.assertEqual(row["verification"],"unverified")
            self.assertFalse(any(k in row for k in ("lat","lon","latitude","longitude","miles","distance")))
        self.assertEqual(by_id[identity_key("Leyton Orient FC")]["postcode"],"E10 5NF")
        self.assertEqual(by_id[identity_key("Rotherham United FC")]["postcode"],"S60 1FJ")
        self.assertNotIn(identity_key("AFC Liverpool"),by_id)
        self.assertNotIn(identity_key("Liverpool FC"),by_id)
        self.assertIn("previewAfcBoundary(c.name,g.name)",updated)
        same,second=transform(updated,self.evidence,self.competition)
        self.assertEqual(same,updated,"Second generator run must not mutate existing results")
        self.assertEqual(second["new_pending"],0)
        self.assertEqual(second["already_pending"],31)

    def test_fail_closed_if_approval_or_identity_drift(self):
        changed=json.loads(json.dumps(self.evidence))
        changed["safety"]["verified_location_badge_authorized"]=True
        with self.assertRaisesRegex(ValueError,"non-promotion"):
            transform(self.source,changed,self.competition)
        changed=json.loads(json.dumps(self.evidence))
        changed["clubs"][0]["postcode"]="XX INVALID"
        with self.assertRaises(ValueError):
            transform(self.source,changed,self.competition)
        changed=json.loads(json.dumps(self.evidence))
        changed["clubs"].append(dict(changed["clubs"][0]))
        with self.assertRaises(ValueError):
            transform(self.source,changed,self.competition)

if __name__=="__main__":
    unittest.main()
