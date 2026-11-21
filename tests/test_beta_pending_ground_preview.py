import unittest
from pathlib import Path
from updater.build_beta_pending_ground_preview import build, ROOT
from updater.audit_active_custodian_locations import array_from_html, identity_key

class PendingGroundPreviewTests(unittest.TestCase):
    def test_preview_does_not_change_approved_sources_or_verification(self):
        original=(ROOT/"beta/clubfinder-beta.html").read_text("utf-8")
        generated, report=build()
        self.assertEqual(report["second_round_missing"],0)
        self.assertEqual(report["already_reviewed_records"],31)
        self.assertEqual(report["staged_preview_records"],0)
        self.assertEqual(report["skipped"],[])
        self.assertTrue(report["read_only_preview"])
        self.assertFalse(report["automatic_verification"])
        self.assertEqual(original,(ROOT/"beta/clubfinder-beta.html").read_text("utf-8"))
        old_ground=array_from_html(original,"GROUNDS")
        new_ground=array_from_html(generated,"GROUNDS")
        self.assertEqual(old_ground,new_ground[:len(old_ground)])
        new_rows=new_ground[len(old_ground):]
        self.assertEqual(len(new_rows),report["staged_preview_records"])
        pending_rows=[x for x in new_ground if x.get("preview_evidence_only")]
        self.assertEqual(len(pending_rows),31)
        for row in pending_rows:
            self.assertEqual(row["verification"],"unverified")
            self.assertTrue(row["preview_evidence_only"])
            self.assertNotIn("lat",row)
            self.assertNotIn("lon",row)
            self.assertNotIn("distance",row)
        self.assertEqual(array_from_html(original,"LAW2_ORIGIN_LOCATIONS"),
                         array_from_html(generated,"LAW2_ORIGIN_LOCATIONS"))
        by_id={identity_key(x["name"]):x for x in pending_rows}
        for name,postcode in [("Leyton Orient FC","E10 5NF"),("Port Vale FC","ST6 1AW"),("Rotherham United FC","S60 1FJ")]:
            self.assertEqual(by_id[identity_key(name)]["postcode"],postcode)
        self.assertNotIn(identity_key("Liverpool FC"),by_id)
        self.assertNotIn(identity_key("AFC Liverpool"),by_id)
if __name__ == "__main__":
    unittest.main()
