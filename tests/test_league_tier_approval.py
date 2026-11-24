"""Isolated approval tests. The real season ledger is only read."""
import copy
import tempfile
import unittest
from datetime import date
from pathlib import Path

from updater.league_tier_approval import (
    LEDGER, active_events, append_decisions, digest, make_manifest,
    manifest_payload, read_json, verify_pinned_manifest, write_json_atomic,
)

AS_OF = date(2026, 11, 24)
LEDGER_EMPTY = {"schema": 1, "season": "2026-27", "events": []}


class LeagueTierApprovalTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            dict(club=name, source_club=source, population="original-clubfinder", approved_tier="",
                 league="Example League", division="Premier", source_fa_step=5, proposed_tier=9,
                 match_status="matched_normalized_initial", source_status="official_initial_allocation",
                 source_url="https://example.org/initial", evidence_required="")
            for name, source in [("One Town FC", "One Town"), ("Two Town FC", "Two Town")]
        ]
        self.evidence = {
            "season": "2026-27",
            "divisions": [dict(league="Example League", division="Premier", teams=["One Town", "Two Town"],
                               source_url="https://example.org/adopted", observed_on="2026-07-21")],
            "individual": [],
            "intervals": [dict(club="One Town FC", league="Example League", division="Premier",
                               proposed_tier=9, valid_from="2026-08-01", valid_until="2026-11-20",
                               source_url="https://example.org/dates", observed_on="2026-11-24",
                               note="Fixture with independently verified effective limits")],
        }

    def manifest(self):
        payload = manifest_payload(self.rows, self.evidence, AS_OF, {"fixture": "fixed"})
        return dict(payload, manifest_sha256=digest(payload))

    def request(self, manifest, decisions=None, batches=None):
        return {
            "manifest_sha256": manifest["manifest_sha256"], "reviewer": "Fixture reviewer",
            "reviewed_at": "2026-11-24T12:00:00+00:00", "decisions": decisions or [],
            "division_batches": batches or [],
        }

    def test_batch_replays_and_never_creates_intervals(self):
        manifest = self.manifest()
        self.assertEqual(manifest, self.manifest())
        batch, = manifest["batches"]
        selection = dict(batch_id=batch["batch_id"], count=2, reason="Checked canonical division")
        request = self.request(manifest, batches=[selection])
        output = append_decisions(LEDGER_EMPTY, manifest, request, AS_OF)
        self.assertEqual(len(output["events"]), 2)
        self.assertEqual({event["scope"] for event in output["events"]}, {"season"})
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "approval-ledger.json"
            write_json_atomic(file, output)
            self.assertEqual(append_decisions(read_json(file), manifest, request, AS_OF), output)

    def test_explicit_holds_and_reproducible_supersession(self):
        manifest = self.manifest()
        hold = dict(club="One Town FC", scope="season", action="hold", reason="Review in progress")
        prior = append_decisions(LEDGER_EMPTY, manifest, self.request(manifest, [hold]), AS_OF)
        old, = prior["events"]
        approval = dict(hold, action="approve", reason="Identity verified", supersedes=old["event_id"])
        new = append_decisions(prior, manifest, self.request(manifest, [approval]), AS_OF)
        self.assertEqual(len(new["events"]), 2)
        active, = active_events(new["events"]).values()
        self.assertEqual(active["action"], "approve")
        self.assertEqual(active["supersedes"], old["event_id"])
        with self.assertRaisesRegex(ValueError, "Conflicting active"):
            append_decisions(prior, manifest, self.request(manifest, [dict(hold, reason="Unrelated")]), AS_OF)

    def test_dated_decisions_require_their_own_proof_and_cannot_overlap(self):
        self.evidence["divisions"] = []
        manifest = self.manifest()
        self.assertIsNone(manifest["entries"]["One Town FC"]["membership_evidence"])
        proof, = manifest["entries"]["One Town FC"]["interval_evidence"]
        interval = dict(club="One Town FC", scope="interval", action="approve", reason="Date evidence checked",
                        valid_from="2026-08-01", valid_until="2026-09-01", interval_sha256=proof["sha256"])
        ledger = append_decisions(LEDGER_EMPTY, manifest, self.request(manifest, [interval]), AS_OF)
        self.assertEqual([r["scope"] for r in ledger["events"]], ["interval"])
        for wrong in [
            dict(interval, valid_from="2026-07-31"), dict(interval, interval_sha256="no proof"),
            dict(interval, valid_until="2026-12-12"),
        ]:
            with self.subTest(wrong=wrong), self.assertRaisesRegex(ValueError, "Unsupported effective dates"):
                append_decisions(LEDGER_EMPTY, manifest, self.request(manifest, [wrong]), AS_OF)
        conflict = dict(interval, valid_from="2026-08-15", valid_until="2026-09-15")
        with self.assertRaisesRegex(ValueError, "Conflicting active"):
            append_decisions(ledger, manifest, self.request(manifest, [conflict]), AS_OF)

    def test_stale_evidence_and_ambiguous_identity_fail_closed(self):
        manifest = self.manifest()
        self.evidence["divisions"].append(dict(self.evidence["divisions"][0], division="North"))
        self.evidence["intervals"] = []
        revised = self.manifest()
        with self.assertRaisesRegex(ValueError, "Stale or altered"):
            verify_pinned_manifest(manifest, revised)
        one = dict(club="One Town FC", scope="season", action="approve", reason="Attempt review")
        with self.assertRaisesRegex(ValueError, "Ambiguous or unsupported"):
            append_decisions(LEDGER_EMPTY, revised, self.request(revised, [one]), AS_OF)
        corrupted = copy.deepcopy(manifest)
        corrupted["entries"]["One Town FC"]["proposed_tier"] = 7
        with self.assertRaisesRegex(ValueError, "Invalid manifest digest"):
            append_decisions(LEDGER_EMPTY, corrupted, self.request(corrupted, [one]), AS_OF)
        self.assertEqual(read_json(LEDGER)["events"], [])

    def test_current_proposal_leaves_boro_unresolved_and_records_no_intervals(self):
        manifest = make_manifest(AS_OF)
        self.assertIsNone(manifest["entries"]["Boro Rangers FC"]["membership_evidence"])
        self.assertIsNone(manifest["entries"]["Cribbs FC"]["membership_evidence"])
        self.assertIsNone(manifest["entries"]["Holmesdale FC"]["membership_evidence"])
        self.assertEqual(manifest["divisions_checked"], 48)
        self.assertEqual(sum(bool(entry["membership_evidence"]) for entry in manifest["entries"].values()), 740)
        self.assertTrue(all(not entry["interval_evidence"] for entry in manifest["entries"].values()))
        self.assertEqual(len(manifest["entries"]), 743)
