"""Prepare pinned reviews and record explicit League & Tier decisions in a separate ledger."""
import argparse
import fcntl
import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from updater.league_tier_readonly import (
    AMENDMENTS, DEFAULT_SOURCES, MATCH_STATUSES, MEMBERSHIP, ROOT, SEASON, build_audit, key,
)
from updater.league_tier_review import match_method

SOURCES = AMENDMENTS.parent
CONFIRMATIONS = SOURCES / "league-tier-2026-27-membership-confirmations.json"
LEDGER = SOURCES / "league-tier-2026-27-approval-ledger.json"
FIELDS = ("league", "division", "proposed_tier")
SEASON_FROM = date(2026, 6, 1)
SEASON_UNTIL = date(2027, 6, 1)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path, value):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as file:
        temp = Path(file.name)
        try:
            json.dump(value, file, ensure_ascii=False, indent=2, sort_keys=True)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
            os.replace(temp, path)
        finally:
            temp.unlink(missing_ok=True)


def iso_day(value):
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError(f"Expected YYYY-MM-DD: {value}")
    return parsed


def check_source(item, as_of):
    url = urlsplit(item["source_url"])
    if url.scheme != "https" or not url.hostname or iso_day(item["observed_on"]) > as_of:
        raise ValueError(f"Invalid or future evidence: {item}")
    if item.get("identity_url"):
        identity = urlsplit(item["identity_url"])
        if identity.scheme != "https" or not identity.hostname:
            raise ValueError(f"Invalid identity evidence: {item}")


def manifest_payload(rows, evidence, as_of, pins):
    if evidence["season"] != SEASON:
        raise ValueError("Membership evidence belongs to a different season")
    divisions = {}
    memberships = defaultdict(set)
    for record in evidence["divisions"]:
        check_source(record, as_of)
        division = record["league"], record["division"]
        names = [key(name) for name in record["teams"]]
        if division in divisions or not names or "" in names or len(set(names)) != len(names):
            raise ValueError(f"Duplicate division, empty or ambiguous official team list: {division}")
        divisions[division] = record
        for name in names:
            memberships[name].add(division)

    individuals = {}
    for item in evidence["individual"]:
        check_source(item, as_of)
        club = item["club"]
        if club in individuals or item["finding"] not in {"confirmed", "hold"} or not item["note"].strip():
            raise ValueError(f"Invalid individual evidence for {club}")
        individuals[club] = item

    entries, batches = {}, defaultdict(list)
    for row in rows:
        club = row["club"]
        if club in entries or row["approved_tier"]:
            raise ValueError(f"Duplicate identity or live approval in input: {club}")
        division = row["league"], row["division"]
        source = divisions.get(division)
        name = key(row["source_club"])
        match = match_method(row)
        cited = individual = None
        reason = ""
        if row["match_status"] not in MATCH_STATUSES:
            reason = row["evidence_required"] or "Unresolved audit identity."
        elif club in individuals or match in {"documented_identity", "documented_publisher_alias", "spelling_normalization"}:
            individual = individuals.get(club)
            if not individual or individual["finding"] == "hold":
                reason = individual["note"] if individual else "Individual identity and season evidence required."
            elif (individual["league"], individual["division"]) != division:
                reason = "Individual evidence conflicts with the candidate division."
            else:
                cited = individual
        elif row["source_status"] == MEMBERSHIP:
            cited = {"source_url": row["source_url"], "observed_on": row["source_as_of"],
                     "source_club": row["source_club"]}
            check_source(cited, as_of)
        elif not source:
            reason = "Official season evidence for this division is missing."
        elif memberships[name] != {division}:
            reason = ("Official lists contain competing memberships; resolve the senior identity."
                      if memberships[name] else "Candidate name is absent from the captured official division lists.")
        else:
            cited = source
        identity_pin = {"season": SEASON, "population": row["population"], "club": club}
        club_id = digest(identity_pin)
        entries[club] = {
            "club_id": club_id, "population": row["population"], "club": club,
            **{field: row[field] for field in FIELDS},
            "fa_step": row["source_fa_step"], "source_club": row["source_club"],
            "candidate_source_url": row["source_url"], "match": match,
            "candidate_identity_resolved": row["match_status"] in MATCH_STATUSES,
            "membership_evidence": ({
                "source_url": cited["source_url"], "observed_on": cited["observed_on"], "sha256": digest(cited),
                "note": cited.get("note", ""), "identity_url": cited.get("identity_url", ""),
            } if cited else None),
            "hold_reason": reason, "interval_evidence": [],
        }
        if cited and individual is None and match in {"exact", "suffix_only"}:
            batches[division].append(club)

    for item in evidence["intervals"]:
        check_source(item, as_of)
        entry = entries[item["club"]]
        start, end = iso_day(item["valid_from"]), iso_day(item["valid_until"])
        if (not entry["candidate_identity_resolved"] or any(entry[f] != item[f] for f in FIELDS)
                or not SEASON_FROM <= start < end <= SEASON_UNTIL
                or end > iso_day(item["observed_on"])
                or not item["note"].strip()):
            raise ValueError(f"Unsupported dated evidence for {item['club']}")
        entry["interval_evidence"].append(dict(item, sha256=digest(item)))

    batch_list = []
    for (league, division), clubs in sorted(batches.items()):
        members = sorted(clubs)
        batch = {"league": league, "division": division, "members": members, "count": len(members)}
        batch["batch_id"] = digest(batch)
        batch_list.append(batch)
    return {
        "schema": 1, "season": SEASON, "as_of": as_of.isoformat(), "pins": pins,
        "entries": entries, "batches": batch_list, "divisions_checked": len(divisions),
        "coverage": dict(sorted(Counter(
            f"{entry['population']} {'season_evidence' if entry['membership_evidence'] else 'hold'}"
            for entry in entries.values()
        ).items())),
    }


def make_manifest(as_of):
    rows, _ = build_audit(as_of=as_of)
    pins = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (*DEFAULT_SOURCES, AMENDMENTS, CONFIRMATIONS)}
    pins["audit_identities"] = digest(sorted((r["population"], r["club"]) for r in rows))
    payload = manifest_payload(rows, read_json(CONFIRMATIONS), as_of, pins)
    return dict(payload, manifest_sha256=digest(payload))


def signed_body(event):
    return {k: v for k, v in event.items() if k != "event_id"}


def active_events(events):
    active = {}
    seen = set()
    for event in events:
        identifier = event["event_id"]
        if identifier in seen or digest(signed_body(event)) != identifier:
            raise ValueError("Corrupt or repeated approval event")
        seen.add(identifier)
        previous = event["supersedes"]
        if previous:
            original = active.get(previous)
            if not original or (original["club_id"], original["scope"]) != (event["club_id"], event["scope"]):
                raise ValueError("Supersession must name an active decision for the same identity and scope")
            del active[previous]
        for other in active.values():
            if (event["club_id"], event["scope"]) != (other["club_id"], other["scope"]):
                continue
            if event["scope"] == "season" or (
                event["valid_from"] < other["valid_until"] and other["valid_from"] < event["valid_until"]
            ):
                raise ValueError(f"Conflicting active decisions for {event['club']}")
        active[identifier] = event
    return active


def decisions_from_request(request, manifest):
    if request["manifest_sha256"] != manifest["manifest_sha256"]:
        raise ValueError("Decision request refers to a stale manifest")
    approved_batches = {batch["batch_id"]: batch for batch in manifest["batches"]}
    decisions = list(request.get("decisions", []))
    if any("batch_id" in decision for decision in decisions):
        raise ValueError("Individual decisions cannot claim division batch provenance")
    for selection in request.get("division_batches", []):
        batch = approved_batches.get(selection["batch_id"])
        if (not batch or batch["count"] != selection["count"] or not selection["reason"].strip()):
            raise ValueError("Division batch ID, club count or review reason did not match")
        decisions.extend({
            "club": club, "scope": "season", "action": "approve", "reason": selection["reason"],
            "batch_id": batch["batch_id"],
        } for club in batch["members"])
    if not decisions:
        raise ValueError("No decisions supplied")
    return decisions


def append_decisions(ledger, manifest, request, today):
    if ledger["schema"] != 1 or ledger["season"] != SEASON:
        raise ValueError("Ledger season or schema mismatch")
    if (manifest["season"] != SEASON
            or manifest["manifest_sha256"] != digest({k: v for k, v in manifest.items() if k != "manifest_sha256"})):
        raise ValueError("Invalid manifest digest")
    reviewed = datetime.fromisoformat(request["reviewed_at"])
    reviewer = request["reviewer"].strip()
    if (not reviewer or reviewed.tzinfo is None
            or not iso_day(manifest["as_of"]) <= reviewed.astimezone(timezone.utc).date() <= today):
        raise ValueError("Reviewer and a valid timezone-aware review timestamp are required")
    events = list(ledger["events"])
    active_events(events)
    seen = {event["event_id"] for event in events}
    for item in decisions_from_request(request, manifest):
        club = item["club"]
        entry = manifest["entries"].get(club)
        scope, action = item["scope"], item["action"]
        reason = item["reason"].strip()
        if not entry or scope not in {"season", "interval"} or action not in {"approve", "hold"} or not reason:
            raise ValueError(f"Invalid decision for {club}")
        start, end = item.get("valid_from", ""), item.get("valid_until", "")
        interval_pin = item.get("interval_sha256", "")
        if scope == "season" and (start or end or interval_pin):
            raise ValueError("A season decision cannot set a dated interval")
        if scope == "interval" and (
            not start or not end or not SEASON_FROM <= iso_day(start) < iso_day(end) <= SEASON_UNTIL
        ):
            raise ValueError("Interval decisions require supported ordered dates inside the season")
        cited = entry["membership_evidence"]
        if action == "approve":
            if scope == "season" and not cited:
                raise ValueError(f"Ambiguous or unsupported identity: {club}")
            if scope == "interval" and not any(
                proof["sha256"] == interval_pin and proof["valid_from"] <= start and end <= proof["valid_until"]
                for proof in entry["interval_evidence"]
            ):
                raise ValueError(f"Unsupported effective dates for {club}")
        event = {
            "club": club, "club_id": entry["club_id"], "scope": scope, "action": action,
            "valid_from": start, "valid_until": end, "interval_sha256": interval_pin,
            "reviewer": reviewer, "reviewed_at": reviewed.isoformat(), "reason": reason,
            "manifest_sha256": manifest["manifest_sha256"], "entry": entry,
            "batch_id": item.get("batch_id", ""), "supersedes": item.get("supersedes", ""),
        }
        identifier = digest(event)
        if identifier not in seen:
            events.append(dict(event, event_id=identifier))
            seen.add(identifier)
    active_events(events)
    return dict(ledger, events=events)


def verify_pinned_manifest(supplied, current):
    if supplied != current:
        raise ValueError("Stale or altered manifest; prepare a new review")


def write_proposal(manifest, path):
    write_json_atomic(path, manifest)
    entries = manifest["entries"].values()
    counts = Counter((entry["population"], "Proposed" if entry["membership_evidence"] else "Hold")
                     for entry in entries)
    report = ["# Proposed League & Tier membership review", "",
              f"Cut-off: {manifest['as_of']}. Manifest SHA-256: `{manifest['manifest_sha256']}`.", "",
              "| Population | Season evidence | Holds |", "| --- | ---: | ---: |"]
    for population in sorted({entry["population"] for entry in entries}):
        report.append(f"| {population} | {counts[population, 'Proposed']} | {counts[population, 'Hold']} |")
    report += ["", "## Named holds", ""]
    for entry in entries:
        if entry["hold_reason"]:
            report.append(f"- **{entry['club']}** — {entry['hold_reason']}")
    report += ["", f"Proposed season-only division batches: {len(manifest['batches'])}.",
               f"Official NLS division lists checked: {manifest['divisions_checked']}.",
               "Dated-interval proposals: " + str(sum(bool(e["interval_evidence"]) for e in entries)) + ".",
               "The proposal records zero approvals.", ""]
    path.with_suffix(".md").write_text("\n".join(report), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--as-of", type=iso_day, required=True)
    prepare.add_argument("--out", type=Path, required=True)
    record = commands.add_parser("record")
    record.add_argument("--manifest", type=Path, required=True)
    record.add_argument("--decisions", type=Path, required=True)
    record.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()
    today = datetime.now(timezone.utc).date()
    if args.command == "prepare":
        if args.as_of > today:
            parser.error("Review cut-off is in the future")
        write_proposal(make_manifest(args.as_of), args.out)
        return
    if args.ledger.resolve() in {args.manifest.resolve(), args.decisions.resolve()}:
        parser.error("Ledger and review inputs must be separate")
    lock_path = Path(tempfile.gettempdir()) / f"tffac-ledger-{digest(str(args.ledger.resolve()))}.lock"
    with lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        supplied = read_json(args.manifest)
        fresh = make_manifest(iso_day(supplied["as_of"]))
        verify_pinned_manifest(supplied, fresh)
        current = read_json(args.ledger)
        result = append_decisions(current, fresh, read_json(args.decisions), today)
        if result != current:
            write_json_atomic(args.ledger, result)


if __name__ == "__main__":
    main()
