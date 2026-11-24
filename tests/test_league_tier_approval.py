"""Isolated approval tests. The real season ledger is only read."""
import copy
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from datetime import date
from pathlib import Path

from updater.league_tier_approval import (
    CONFIRMATIONS, LEDGER, active_events, append_decisions, digest,
    manifest_payload, read_json, verify_pinned_manifest, write_json_atomic,
)
from updater.league_tier_readonly import AMENDMENTS, COMPANION, DEFAULT_SOURCES, ROOT, ROSTER, key

AS_OF = date(2026, 11, 24)
LEDGER_EMPTY = {"schema": 1, "season": "2026-27", "events": []}
PHASE_5_DIGEST = "e77fec695e631789c0835ae53895cabda8b27de502ae77e0a9734d45709eaddb"
FORMAL_REQUEST = LEDGER.with_name("league-tier-2026-27-season-approval-request.json")


def canonical_sha256(data):
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


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
        individual = dict(club="One Town FC", scope="season", action="approve",
                          reason="Individual review", batch_id=batch["batch_id"])
        with self.assertRaisesRegex(ValueError, "division batch provenance"):
            append_decisions(LEDGER_EMPTY, manifest, self.request(manifest, [individual]), AS_OF)

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
        for ledger, replacement in (
            (new, dict(approval, reason="Already superseded")),
            (prior, dict(approval, club="Two Town FC")),
            (prior, dict(approval, action="hold", scope="interval",
                         valid_from="2026-08-01", valid_until="2026-09-01")),
        ):
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, "identity and scope"):
                append_decisions(ledger, manifest, self.request(manifest, [replacement]), AS_OF)

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


class LeagueTierAcceptanceTests(unittest.TestCase):
    def cli(self, *args, error=None):
        result = subprocess.run(
            [sys.executable, "-m", "updater.league_tier_approval", *map(str, args)],
            cwd=ROOT, text=True, capture_output=True, timeout=60,
        )
        if error:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(error, result.stderr)
        else:
            self.assertEqual(result.returncode, 0, result.stderr)

    def verify_proposal(self, manifest):
        payload = {field: value for field, value in manifest.items() if field != "manifest_sha256"}
        self.assertEqual(manifest["manifest_sha256"], canonical_sha256(payload))
        self.assertEqual(manifest["manifest_sha256"], PHASE_5_DIGEST)
        with ROSTER.open(encoding="utf-8-sig", newline="") as roster:
            originals = [row["Club"].strip() for row in csv.DictReader(roster)]
        original_keys = {key(name) for name in originals}
        companions = [row["club"].strip() for row in read_json(COMPANION)["clubs"]
                      if key(row["club"]) not in original_keys]
        self.assertEqual((len(originals), len(companions)), (651, 92))
        population = dict.fromkeys(originals, "original-clubfinder")
        population.update(dict.fromkeys(companions, "companion-journey-registry"))
        entries = manifest["entries"]
        self.assertEqual(len(population), 743)
        self.assertEqual({club: entry["population"] for club, entry in entries.items()}, population)
        self.assertEqual({club: entry["club"] for club, entry in entries.items()},
                         {club: club for club in population})
        ids = {canonical_sha256(dict(season="2026-27", population=group, club=club))
               for club, group in population.items()}
        self.assertEqual(len(ids), 743)
        for club, entry in entries.items():
            self.assertEqual(entry["club_id"], canonical_sha256(
                dict(season="2026-27", population=population[club], club=club)))
            self.assertFalse(entry["interval_evidence"])
        pins = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in (*DEFAULT_SOURCES, AMENDMENTS, CONFIRMATIONS)}
        pins["audit_identities"] = canonical_sha256(sorted((group, club) for club, group in population.items()))
        self.assertEqual(manifest["pins"], pins)

        evidence = read_json(CONFIRMATIONS)
        divisions = {(row["league"], row["division"]): row for row in evidence["divisions"]}
        individuals = {row["club"]: row for row in evidence["individual"] if row["finding"] == "confirmed"}
        self.assertEqual(manifest["divisions_checked"], len(divisions))
        self.assertEqual(len(divisions), 48)
        professional = {}
        for path in DEFAULT_SOURCES:
            with path.open(encoding="utf-8-sig", newline="") as file:
                for row in csv.DictReader(file):
                    if row["source_status"] == "official_season_membership":
                        self.assertEqual(row["season"], "2026-27")
                        professional[row["league"], row["division"], row["club"]] = row
        self.assertEqual(Counter(row["tier"] for row in professional.values()),
                         {"1": 20, "2": 24, "3": 24, "4": 24})
        approved = {club for club, entry in entries.items() if entry["membership_evidence"]}
        for club in approved:
            entry = entries[club]
            division = entry["league"], entry["division"]
            tier, step = entry["proposed_tier"], entry["fa_step"]
            if step:
                self.assertEqual(tier, step + 4, club)
            else:
                self.assertEqual(tier, int(professional[(*division, entry["source_club"])]["tier"]), club)
            if club in individuals:
                source = individuals[club]
                self.assertEqual(division, (source["league"], source["division"]), club)
            elif not step:
                row = professional[(*division, entry["source_club"])]
                source = dict(source_url=row["source_url"], observed_on=row["source_as_of"], source_club=row["club"])
            else:
                source = divisions[division]
                self.assertIn(key(entry["source_club"]), {key(name) for name in source["teams"]}, club)
            pin = entry["membership_evidence"]
            self.assertEqual(pin["sha256"], canonical_sha256(source), club)
            self.assertEqual((pin["source_url"], pin["observed_on"]), (source["source_url"], source["observed_on"]), club)

        batches = manifest["batches"]
        batched = []
        for batch in batches:
            self.assertEqual(batch["batch_id"], canonical_sha256(
                {field: value for field, value in batch.items() if field != "batch_id"}))
            self.assertEqual(batch["count"], len(batch["members"]))
            for club in batch["members"]:
                entry = entries[club]
                self.assertIn(entry["match"], {"exact", "suffix_only"})
                self.assertEqual((entry["league"], entry["division"]), (batch["league"], batch["division"]))
            batched.extend(batch["members"])
        self.assertEqual(len(batches), 35)
        self.assertEqual(len({batch["batch_id"] for batch in batches}), 35)
        self.assertEqual(len(batched), 698)
        self.assertEqual(len(set(batched)), 698)
        self.assertTrue(set(batched) <= approved)
        individual = approved - set(batched)
        self.assertEqual(len(individual), 42)
        self.assertEqual(individual, individuals.keys())
        holds = {club: entry["hold_reason"] for club, entry in entries.items() if entry["hold_reason"]}
        self.assertEqual(set(holds), {"Boro Rangers FC", "Cribbs FC", "Holmesdale FC"})
        self.assertEqual(set(holds), entries.keys() - approved)
        self.assertEqual(Counter(population[club] for club in approved),
                         {"original-clubfinder": 648, "companion-journey-registry": 92})
        return individual, holds

    def verify_season_events(self, events, manifest, individual, holds):
        self.assertEqual(Counter((event["scope"], event["action"]) for event in events),
                         {("season", "approve"): 740, ("season", "hold"): 3})
        self.assertEqual(Counter(event["club"] for event in events), dict.fromkeys(manifest["entries"], 1))
        self.assertEqual({event["club"] for event in events if event["action"] == "hold"}, holds.keys())
        self.assertEqual({event["club"]: event["batch_id"] for event in events if event["batch_id"]},
                         {club: batch["batch_id"] for batch in manifest["batches"] for club in batch["members"]})
        self.assertEqual({event["club"] for event in events if event["action"] == "approve"
                          and not event["batch_id"]}, individual)
        self.assertEqual(set(active_events(events)), {event["event_id"] for event in events})
        for event in events:
            self.assertEqual(event["entry"], manifest["entries"][event["club"]])
            self.assertEqual(event["club_id"], event["entry"]["club_id"])
            self.assertEqual(event["manifest_sha256"], PHASE_5_DIGEST)
            self.assertFalse(event["valid_from"] or event["valid_until"] or event["interval_sha256"])

    def test_formal_season_ledger_replays_from_checked_in_request(self):
        committed = LEDGER.read_bytes()
        with tempfile.TemporaryDirectory(prefix="tffac-league-tier-formal-") as directory:
            proposal, replay = Path(directory) / "proposal.json", Path(directory) / "ledger.json"
            self.cli("prepare", "--as-of", AS_OF, "--out", proposal)
            manifest = read_json(proposal)
            individual, holds = self.verify_proposal(manifest)
            request = read_json(FORMAL_REQUEST)
            self.assertEqual(request["reviewer"], "Anvil Springstien (GitHub: anvilspringstien)")
            self.assertEqual(len(request["division_batches"]), 35)
            self.assertEqual(len(request["decisions"]), 45)
            events = json.loads(committed)["events"]
            self.verify_season_events(events, manifest, individual, holds)
            for event in events:
                self.assertEqual(event["reviewer"], request["reviewer"])
                self.assertEqual(event["reviewed_at"], request["reviewed_at"])
                self.assertIn("Project owner authorised formal season decisions for PR #732", event["reason"])
                if event["action"] == "hold":
                    self.assertTrue(event["reason"].endswith(holds[event["club"]]))
            write_json_atomic(replay, LEDGER_EMPTY)
            for _ in range(2):
                self.cli("record", "--manifest", proposal, "--decisions", FORMAL_REQUEST, "--ledger", replay)
                self.assertEqual(replay.read_bytes(), committed)
        self.assertEqual(LEDGER.read_bytes(), committed)

    def test_phase_5_proposal_replays_in_isolation(self):
        before = LEDGER.read_bytes()
        with tempfile.TemporaryDirectory(prefix="tffac-league-tier-acceptance-") as directory:
            tmp = Path(directory)
            proposal, request_file = tmp / "proposal.json", tmp / "request.json"
            self.cli("prepare", "--as-of", AS_OF, "--out", proposal)
            manifest = read_json(proposal)
            individual, holds = self.verify_proposal(manifest)
            request = {
                "manifest_sha256": manifest["manifest_sha256"],
                "reviewer": "Isolated acceptance fixture",
                "reviewed_at": "2026-11-24T12:00:00+00:00",
                "division_batches": [
                    dict(batch_id=batch["batch_id"], count=batch["count"], reason="Isolated batch replay")
                    for batch in manifest["batches"]
                ],
                "decisions": [
                    dict(club=club, scope="season", action="approve", reason="Isolated individual replay")
                    for club in sorted(individual)
                ] + [
                    dict(club=club, scope="season", action="hold", reason=reason)
                    for club, reason in sorted(holds.items())
                ],
            }
            write_json_atomic(request_file, request)
            ledgers = [tmp / "ledger.json", tmp / "replay.json"]
            for ledger in ledgers:
                write_json_atomic(ledger, LEDGER_EMPTY)
                self.cli("record", "--manifest", proposal, "--decisions", request_file, "--ledger", ledger)
            ledger, replay = ledgers
            accepted = ledger.read_bytes()
            self.assertEqual(accepted, replay.read_bytes())
            self.cli("record", "--manifest", proposal, "--decisions", request_file, "--ledger", ledger)
            self.assertEqual(accepted, ledger.read_bytes())
            events = read_json(ledger)["events"]
            self.verify_season_events(events, manifest, individual, holds)
            self.assertEqual({event["club"]: event["reason"] for event in events if event["action"] == "hold"},
                             holds)
            altered = tmp / "stale-proposal.json"
            manifest["pins"]["audit_identities"] = "0" * 64
            del manifest["manifest_sha256"]
            manifest["manifest_sha256"] = canonical_sha256(manifest)
            write_json_atomic(altered, manifest)
            self.cli("record", "--manifest", altered, "--decisions", request_file, "--ledger", ledger,
                     error="Stale or altered manifest")
            self.assertEqual(accepted, ledger.read_bytes())
            request["division_batches"] = []
            request["decisions"] = [
                dict(club=min(individual), scope="interval", action="approve", reason="Isolated date rejection",
                     valid_from="2026-08-01", valid_until="2026-08-02"),
            ]
            write_json_atomic(request_file, request)
            self.cli("record", "--manifest", proposal, "--decisions", request_file, "--ledger", ledger,
                     error="Unsupported effective dates")
            self.assertEqual(accepted, ledger.read_bytes())
        self.assertEqual(LEDGER.read_bytes(), before)
