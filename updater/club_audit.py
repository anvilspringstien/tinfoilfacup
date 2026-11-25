"""Build a read-only Mission Control club audit from versioned repository sources."""
import argparse
import json
import math
import subprocess
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from updater.apply_beta_current_ground_names import literal
from updater.audit_active_custodian_locations import (
    ROOT, array_from_html, display_key, identity_key, next_round_entrants,
)
from updater.club_entry_radar import inspect_rounds
from updater.league_tier_approval import LEDGER, active_events, digest, iso_day
from updater.league_tier_readonly import SEASON, key, load_population
from updater.league_tier_review import cup_observations
from updater.round_state_engine import TEAM_IDENTITY_ALIASES

BUILDS = {"public": "clubfinder.html", "beta": "beta/clubfinder-beta.html"}
ROSTER = "tester-club-postcodes.csv"
JOURNEY = "journey-club-registry.json"
COMPETITION = "competition.json"
APPROVALS = LEDGER.relative_to(ROOT).as_posix()
CURRENT_NAMES = "updater/current-ground-name-ledger.json"
VERIFIED_LOCATIONS = "updater/law2-verified-location-ledger.json"
ENTRANT_LOCATIONS = "updater/entrant-home-ground-evidence-2026.json"
IDENTITY_REVIEWS = "updater/identity-variant-confirmation.json"
OPEN_REVIEWS = "updater/club-audit-open-location-reviews.json"
WEBSITE_QUEUE = "updater/club_website_queue.js"
WEBSITE_SNAPSHOT = "updater/club_website_audit_queue.json"
WEBSITE_CLI = "updater/club_website_bulk_promote.js"
LOCATION_FIELDS = ("ground", "postcode", "coordinates")
LOGIC = (
    "updater/club_audit.py", "updater/club_entry_radar.py",
    "updater/audit_active_custodian_locations.py", "updater/round_state_engine.py",
    "updater/league_tier_readonly.py", "updater/league_tier_review.py",
    "updater/league_tier_approval.py", "updater/apply_beta_current_ground_names.py",
    WEBSITE_QUEUE, WEBSITE_CLI,
)


class Sources:
    def __init__(self, root):
        self.root = root
        self.revisions = {}

    def read(self, path):
        data = (self.root / path).read_bytes()
        self.revisions[path] = sha256(data).hexdigest()
        return data.decode("utf-8")

    def json(self, path):
        return json.loads(self.read(path))


def coordinates(row):
    values = (row.get("lat"), row.get("lon"))
    if not all(type(x) in (int, float) and math.isfinite(x) for x in values):
        return None
    lat, lon = values
    return {"lat": lat, "lon": lon} if abs(lat) <= 90 and abs(lon) <= 180 else None


def field(value, status, review_status, evidence=(), **extra):
    return {"value": value, "status": status, "review_status": review_status,
            "evidence": list(evidence), **extra}


def location_index(html):
    index = defaultdict(list)
    for layer in ("GROUNDS", "LAW2_ORIGIN_LOCATIONS"):
        for row in array_from_html(html, layer):
            index[display_key(row.get("name") or row.get("club"))].append((layer, row))
    return index


def location_fields(club, path, index, reviews):
    surrounding = index.get(display_key(club), [])
    exact = [(layer, row) for layer, row in surrounding
             if identity_key(row.get("name") or row.get("club")) == identity_key(club)]
    if len(exact) != 1:
        status = "conflict" if len(exact) > 1 else "ambiguous" if surrounding else "missing"
        return {"record_status": status, **{
            name: field(None, status, "unreviewed", reviews[name],
                        matching_labels=sorted({r.get("name") or r.get("club")
                                                for _, r in (exact or surrounding)}))
            for name in LOCATION_FIELDS
        }}
    layer, row = exact[0]
    recorded_verification = row.get("verification") or "not_declared"
    values = {name: row.get(name) or None for name in ("ground", "postcode")}
    values["coordinates"] = coordinates(row)
    fields = {}
    for name, value in values.items():
        published = {"source": path, "section": layer, "value": value,
                     "status": recorded_verification}
        source_field = "coordinate_source" if name == "coordinates" else "ground_source"
        # Ground-source provenance describes the name/address, never the venue pin.
        provenance = row.get(source_field) or (row.get("source") if name != "coordinates" else None)
        if provenance:
            published["provenance"] = provenance
        decision = next((proof["status"] for proof in reviews[name]
                         if value is not None and proof.get("value") == value
                         and proof["status"] in {"club_confirmed", "verified", "official_source_confirmed"}), None)
        status = "recorded" if value is not None else "missing"
        if name == "coordinates" and value is None and any(row.get(k) is not None for k in ("lat", "lon")):
            status = "invalid"
        if name == "coordinates":
            review_status = ("pending" if value is None else
                             "recorded_with_provenance" if provenance else "recorded_no_provenance")
        else:
            review_status = decision or (recorded_verification if value is not None else "unreviewed")
        fields[name] = field(value, status, review_status, [published, *reviews[name]])
    return {"record_status": "recorded", **fields}


def location_evidence(sources, season):
    fields = defaultdict(lambda: {name: [] for name in LOCATION_FIELDS})
    groupings = (
        (CURRENT_NAMES, "approved", "club", "current_name", "club_confirmed"),
        (VERIFIED_LOCATIONS, "verified_locations", "club", "ground", "verified"),
        (ENTRANT_LOCATIONS, "clubs", "official_identity", "ground", "official_source_confirmed"),
    )
    for path, collection, identity, ground, status in groupings:
        ledger = sources.json(path)
        if ledger.get("season", season) != season:
            raise ValueError(f"Location evidence belongs to a different season: {path}")
        for row in ledger[collection]:
            refs = row.get("public_sources") or [p["url"] for p in row.get("sources", []) if p.get("url")]
            refs = refs or [row[k] for k in ("official_home_ground_source", "supporting_official_source") if row.get(k)]
            proof = {"source": path, "section": collection, "status": row.get("status", status),
                     "urls": refs, "reviewed_on": row.get("reviewed_on") or row.get("verified_at")}
            if path == ENTRANT_LOCATIONS:
                proof["status"] = ("official_source_confirmed"
                                   if row.get("source_review") == "official-ground-and-postcode-confirmed"
                                   else row.get("source_review") or "pending")
                proof["publication_review"] = row.get("review_status")
                pin = coordinates(row.get("coordinates") or {})
                fields[identity_key(row[identity])]["coordinates"].append(
                    dict(proof, status=row.get("coordinates_review") or "pending", value=pin))
            for name, column in (("ground", ground), ("postcode", "postcode")):
                if row.get(column):
                    review = proof["status"]
                    if path == CURRENT_NAMES:
                        name_changed = row["previous_name"] != row["current_name"]
                        postcode_changed = row.get("previous_postcode", row["postcode"]) != row["postcode"]
                        if (name == "ground" and postcode_changed and not name_changed
                                or name == "postcode" and name_changed and not postcode_changed):
                            review = "retained"
                    fields[identity_key(row[identity])][name].append(
                        dict(proof, status=review, value=row[column]))
    return fields


def website_evidence(sources):
    reviews, aliases = defaultdict(list), []
    for path in sorted((sources.root / "updater").glob("club_website_verified_batch_*.json")):
        relative = path.relative_to(sources.root).as_posix()
        ledger = sources.json(relative)
        for section in ("verified", "held", "withdrawn"):
            for row in ledger.get(section, []):
                labels = [row["club"], *row.get("aliases", [])]
                status = row.get("status") or section
                proof = {"source": relative, "section": section, "status": status,
                         "url": row.get("url") or row.get("candidate_url"),
                         "evidence_urls": sorted(set(filter(None, [
                             row.get("evidence_url"), *row.get("evidence_urls", []),
                             *row.get("corroboration_urls", []),
                         ]))),
                         "reviewed_on": row.get("reviewed_on") or row.get("verified_on") or ledger.get("verified_on"),
                         "reason": row.get("reason") or row.get("verification_notes"),
                         "next_step": row.get("next_step")}
                for label in sorted({identity_key(label) for label in labels}):
                    reviews[label].append(proof)
                if status in {"verified_official_club_site", "club_confirmed_offline"}:
                    aliases.extend((row["club"], alias, "website", relative) for alias in labels[1:])
    return reviews, aliases


def website_field(club, path, websites, evidence, queue_rows):
    by_label = {name: url for name, url in websites.items() if identity_key(name) == identity_key(club)}
    urls = sorted(set(by_label.values()))
    url = urls[0] if len(urls) == 1 else None
    latest = max((p["reviewed_on"] or "" for p in evidence if p["section"] != "held"), default="")
    withdrawn = any(p["status"] == "club_confirmed_offline" and (p["reviewed_on"] or "") == latest
                    for p in evidence)
    held = any(p["section"] == "held" for p in evidence)
    matches = [p for p in evidence if p["url"] == url and p["status"] == "verified_official_club_site"]
    status = "conflict" if len(urls) > 1 else "recorded" if url else "missing"
    has_verified_destination = any(p["status"] == "verified_official_club_site" for p in evidence)
    review = ("conflicting_mappings" if len(urls) > 1 else "withdrawn_mapped" if withdrawn and url
              else "withdrawn" if withdrawn else "verified" if matches
              else "verified_unmapped" if not url and has_verified_destination
              else "held" if held else "unreviewed")
    return field(url, status, review, [{"source": path, "section": "CLUB_WEBSITES",
                                       "mappings": by_label}, *evidence],
                 queue_status=queue_rows)


def website_queue(root):
    # Use the existing CLI to regenerate the queue without touching its committed snapshot.
    with TemporaryDirectory(prefix="tffac-club-audit-") as directory:
        path = Path(directory) / "queue.json"
        subprocess.run(["node", str(root / WEBSITE_QUEUE), "--out", str(path)],
                       cwd=root, check=True, stdout=subprocess.DEVNULL)
        return json.loads(path.read_text(encoding="utf-8"))


def identity_index(population):
    index = {}
    for row in population:
        club = row["club"]
        normalized = identity_key(club)
        if not normalized or normalized in index:
            raise ValueError(f"Ambiguous registry identity: {club}")
        index[normalized] = club
    return index


def read_approvals(sources, ids, season):
    ledger = sources.json(APPROVALS)
    if ledger["schema"] != 1 or ledger["season"] != season:
        raise ValueError("Approval ledger schema or season mismatch")
    decisions = defaultdict(list)
    unmatched = []
    for event in active_events(ledger["events"]).values():
        club = event["club"]
        entry = event["entry"]
        if club not in ids or event["club_id"] != ids[club]:
            unmatched.append({"club": club, "event_id": event["event_id"],
                              "reason": "Approval identity is absent from, or differs from, the current population."})
        elif (entry["club"] != club or entry["club_id"] != event["club_id"]
              or event["scope"] not in {"season", "interval"} or event["action"] not in {"approve", "hold"}):
            raise ValueError(f"Invalid active decision for {club}")
        else:
            decisions[club].append(event)
    return decisions, sorted(unmatched, key=lambda row: (row["club"], row["event_id"]))


def decision_details(event):
    if not event:
        return None
    evidence = event["entry"]["membership_evidence"]
    return {"source": APPROVALS, "event_id": event["event_id"], "action": event["action"],
            "reviewed_at": event["reviewed_at"], "evidence": evidence,
            "reason": event["entry"].get("hold_reason") or event["reason"]}


def league_fields(decisions, dates, identity_holds, date_holds):
    season = next((e for e in decisions if e["scope"] == "season"), None)
    approved = season and season["action"] == "approve"
    entry = season["entry"] if approved else {}
    membership = {"status": "approved" if approved else "held" if season else "missing",
                  "league": entry.get("league"), "division": entry.get("division"),
                  "tier": entry.get("proposed_tier"), "fa_step": entry.get("fa_step") or None,
                  "decision": decision_details(season)}
    approvals = []
    for event in sorted((e for e in decisions if e["scope"] == "interval"),
                        key=lambda e: (e["valid_from"], e["event_id"])):
        evidence = next((proof for proof in event["entry"]["interval_evidence"]
                         if proof["sha256"] == event["interval_sha256"]), None)
        if event["action"] == "approve" and evidence is None:
            raise ValueError(f"Unproven interval approval: {event['club']}")
        approvals.append({"source": APPROVALS, "event_id": event["event_id"], "action": event["action"],
                          "valid_from": event["valid_from"], "valid_until": event["valid_until"],
                          "reason": event["reason"], "evidence": evidence})
    played = []
    for day in sorted(dates):
        day = day.isoformat()
        interval = next((e for e in approvals if e["valid_from"] <= day < e["valid_until"]), None)
        status = {"approve": "approved", "hold": "held"}[interval["action"]] if interval else "not_approved"
        played.append({"date": day, "status": status,
                       "event_id": interval["event_id"] if interval else None})
    return membership, {"status": ("has_interval_decisions" if approvals else "not_approved"),
                        "interval_decisions": approvals, "played_dates": played,
                        "identity_holds": sorted(identity_holds), "date_holds": sorted(date_holds)}


def round_history(radar, population, competition_aliases):
    normalized = identity_index(population)
    rules = defaultdict(set)
    # Only explicitly listed round-engine mappings, never its prefix matcher.
    for prefix in ("", "afc "):
        for label, target in TEAM_IDENTITY_ALIASES.items():
            for candidate, club in normalized.items():
                if candidate in (prefix + target, prefix + label):
                    rules[prefix + label].add(club)
                    rules[prefix + target].add(club)
    for club, alias, _, _ in competition_aliases:
        rules[identity_key(alias)].add(club)

    history, unresolved = defaultdict(list), defaultdict(list)
    for group in radar["rounds"]:
        for row in group["clubs"]:
            label, name_key = row["club"], row["identity"]
            candidates = set(rules[name_key])
            if name_key in normalized:
                candidates.add(normalized[name_key])
            observed = {"round": group["round"], "label": label}
            if len(candidates) == 1:
                club = next(iter(candidates))
                method = "identity_key" if normalized.get(name_key) == club else "reviewed_alias"
                history[club].append(dict(observed, match=method))
            else:
                unresolved[label].append(dict(observed, status="ambiguous" if candidates else "unregistered",
                                              candidate_clubs=sorted(candidates)))
    return history, [item for label in sorted(unresolved) for item in unresolved[label]]


def discrepancies(club, published, membership, open_reviews):
    issues = []
    for name in (*LOCATION_FIELDS, "website"):
        public, beta = (published[build][name] for build in BUILDS)
        if public["value"] != beta["value"]:
            issues.append({"field": name, "code": "builds_differ", "reason": "Public and BETA values differ.",
                           "public": public["value"], "beta": beta["value"]})
        for build, state in (("public", public), ("beta", beta)):
            if state["status"] in {"conflict", "ambiguous", "invalid"}:
                issues.append({"field": name, "code": state["status"], "build": build,
                               "reason": "The source does not supply a unique usable value."})
            if name == "website" and state["review_status"] in {"held", "withdrawn_mapped"}:
                issues.append({"field": name, "code": state["review_status"], "build": build,
                               "reason": "Website evidence needs review. See the dated website evidence."})
            if name == "coordinates" and published[build]["record_status"] == "recorded" and state["status"] == "missing":
                issues.append({"field": name, "code": "coordinates_pending", "build": build,
                               "reason": "The ground record has no usable venue coordinates."})
            if name in ("ground", "postcode") and state["value"] is not None:
                for p in state["evidence"]:
                    if (p.get("status") == "club_confirmed" and p["value"] != state["value"]):
                        issues.append({"field": name, "code": "club_confirmation_differs", "build": build,
                                       "reason": "The build differs from the current club-confirmed value.",
                                       "source": p["source"], "observed_value": p["value"]})
    if membership["status"] == "held":
        issues.append({"field": "league_tier", "code": "season_membership_held",
                       "reason": membership["decision"]["reason"]})
    issues.extend(open_reviews.get(club, []))
    return issues


def build_report(root=ROOT, generated_on=None):
    root = Path(root).resolve()
    sources = Sources(root)
    generated_on = generated_on or datetime.now(timezone.utc).date()
    comp = sources.json(COMPETITION)
    season = comp["season"]
    if season != SEASON:
        raise ValueError(f"Unsupported season: {season}")
    journey = sources.json(JOURNEY)
    sources.read(ROSTER)
    population, original_count = load_population(root / ROSTER, root / JOURNEY)
    ids = {r["club"]: digest({"club": r["club"], "population": r["population"], "season": season})
           for r in population}
    original_names = {r["club"] for r in population if r["population"] == "original-clubfinder"}
    registry = {key(r["club"]): r for r in journey["clubs"]}
    if len(registry) != len(journey["clubs"]):
        raise ValueError("Ambiguous Journey registry identities")
    decisions, unmatched = read_approvals(sources, ids, season)
    html = {build: sources.read(path) for build, path in BUILDS.items()}
    eligible = {}
    for build, data in html.items():
        names = [r["name"] for r in array_from_html(data, "ELIGIBLE")]
        if len(set(names)) != len(names):
            raise ValueError(f"Duplicate eligible names in {build}")
        eligible[build] = set(names)
    locations = {build: location_index(data) for build, data in html.items()}
    mappings = {build: literal(data, "CLUB_WEBSITES")[2] for build, data in html.items()}
    location_reviews = location_evidence(sources, season)
    sites, site_aliases = website_evidence(sources)
    queue = website_queue(root)
    queue_snapshot_matches = queue == sources.json(WEBSITE_SNAPSHOT)
    queue_index = defaultdict(set)
    for row in queue["rows"]:
        for label in row["identities"]:
            queue_index[identity_key(label)].add(row["status"])

    alias_claims = defaultdict(set)
    competition_aliases = []
    for row in sources.json(IDENTITY_REVIEWS)["records"]:
        if row["decision"] == "IDENTITY_CONFIRMED" and row["club"] in ids:
            competition_aliases.append((row["club"], row["fchd_match"], "reviewed_identity", IDENTITY_REVIEWS))
    for club, alias, scope, source in [*competition_aliases, *site_aliases]:
        if club in ids and alias != club:
            alias_claims[club].add((alias, scope, source))
    for club, events in decisions.items():
        for event in events:
            label = event["entry"]["source_club"]
            if event["scope"] == "season" and event["action"] == "approve" and label and label != club:
                alias_claims[club].add((label, "league_publisher", APPROVALS))
    radar = inspect_rounds(comp, html, journey)
    history, unassigned = round_history(radar, population, competition_aliases)
    # The League review already keeps ambiguous labels and date conflicts separate.
    labels = [{"club": club, "source_club": label} for club in ids
              for label in ({club} | {row["label"] for row in history[club]}
                            | {claim[0] for claim in alias_claims[club] if claim[1] == "league_publisher"})]
    competition_day = date.fromisoformat(comp["updated_at"][:10])
    dates, ambiguous_dates, date_holds, unmatched_played = cup_observations(comp, labels, competition_day)
    open_reviews = defaultdict(list)
    open_review_data = sources.json(OPEN_REVIEWS)
    if open_review_data["schema_version"] != 1 or open_review_data["season"] != season:
        raise ValueError("Open location review schema or season mismatch")
    unmatched_reviews = []
    for row in open_review_data["reviews"]:
        if row["club"] not in ids:
            unmatched_reviews.append(row)
        else:
            item = {k: v for k, v in row.items() if k != "club"}
            open_reviews[row["club"]].append(item)
            location_reviews[identity_key(row["club"])][row["field"]].append({
                "source": OPEN_REVIEWS, "status": "open_source_discrepancy", "urls": [row["source"]],
                "value": row["observed_value"], "review_reference": row["review_reference"],
            })

    records = []
    for row in sorted(population, key=lambda r: (r["club"].casefold(), r["club"])):
        club = row["club"]
        club_key = identity_key(club)
        companion = registry.get(key(club))
        claim_aliases = set(alias_claims[club])
        for observation in history[club]:
            if observation["label"] != club:
                claim_aliases.add((observation["label"], "competition", COMPETITION))
        published = {}
        for build, path in BUILDS.items():
            published[build] = location_fields(club, path, locations[build], location_reviews[club_key])
            published[build]["website"] = website_field(
                club, path, mappings[build], sites[club_key], sorted(queue_index[club_key]) if build == "beta" else [])
        league, tie_day = league_fields(decisions[club], dates[club], ambiguous_dates[club], date_holds[club])
        records.append({
            "club_id": ids[club], "club": club, "season": season,
            "aliases": [{"label": label, "scope": scope, "source": source}
                        for label, scope, source in sorted(claim_aliases)],
            "membership": {"population": row["population"], "original_clubfinder": club in original_names,
                           "eligible_in": {build: club in names for build, names in eligible.items()},
                           "companion_journey_registry": companion is not None,
                           "companion_label": companion["club"] if companion else None,
                           "companion_state": companion["registry_state"] if companion else None},
            "competition": {"entry_round": row["entry_round"] or None,
                            "companion_entry_round": companion["entry_round"] if companion else None,
                            "observed_rounds": history[club],
                            "supporting_home_ground_evidence": companion.get("supporting_ground_evidence", []) if companion else []},
            "published": published, "league_tier": league, "tie_day": tie_day,
            "discrepancies": discrepancies(club, published, league, open_reviews),
        })
    for path in LOGIC:
        sources.read(path)
    # Preserve the established custodian metric: distinct Second Round Proper
    # participants with no unique identity-matched ground record, per build.
    second_round = next_round_entrants(comp)
    gaps = {build: sorted(label for label in second_round.values()
                          if sum(identity_key(r.get("name") or r.get("club")) == identity_key(label)
                                 for _, r in index.get(display_key(label), [])) != 1)
            for build, index in locations.items()}
    summary = {
        "identities": len(records), "original_clubfinder_identities": original_count,
        "companion_only_identities": len(records) - original_count,
        "companion_registry_entries": len(registry), "season_memberships": dict(sorted(Counter(
            row["league_tier"]["status"] for row in records).items())),
        "tie_day_interval_approvals": sum(d["action"] == "approve" for row in records
                                          for d in row["tie_day"]["interval_decisions"]),
        "eligible_website_coverage": {
            build: {"eligible": len(names), "linked": sum(bool(mappings[build].get(name)) for name in names)}
            for build, names in eligible.items()},
        "canonical_website_queue": {"eligible": queue["eligible"], "eligible_linked": queue["eligible_linked"],
                                    "committed_snapshot_matches": queue_snapshot_matches},
        "ground_record_gaps": {
            "all_identities": {build: sum(row["published"][build]["record_status"] != "recorded"
                                         for row in records) for build in BUILDS},
            "second_round_proper": {"participants": len(second_round),
                                    "missing": {build: len(values) for build, values in gaps.items()},
                                    "clubs": gaps}},
    }
    if summary["eligible_website_coverage"]["beta"] != {
        "eligible": queue["eligible"], "linked": queue["eligible_linked"],
    }:
        raise ValueError("BETA website map and canonical live queue disagree")
    reconciliation = {
        "source_only_round_observations": unassigned,
        "unmatched_played_labels": unmatched_played,
        "unmatched_league_tier_decisions": unmatched,
        "unmatched_open_location_reviews": unmatched_reviews,
        "eligible_roster_differences": {
            build: {"roster_only": sorted(original_names - names), "build_only": sorted(names - original_names)}
            for build, names in eligible.items()},
    }
    return {"schema_version": 1, "read_only": True, "season": season, "generated_on": generated_on.isoformat(),
            "competition_updated_at": comp["updated_at"], "source_revisions": dict(sorted(sources.revisions.items())),
            "summary": summary, "reconciliation": reconciliation,
            "selection": {"mode": "all", "returned": len(records)}, "clubs": records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-on", type=iso_day, help="Override the UTC generation date for reproducibility")
    parser.add_argument("--club", action="append", help="Return this exact registry name; repeat for an excerpt")
    args = parser.parse_args()
    report = build_report(generated_on=args.generated_on)
    if args.club:
        selected = set(args.club)
        report["clubs"] = [row for row in report["clubs"] if row["club"] in selected]
        missing = selected - {row["club"] for row in report["clubs"]}
        if missing:
            parser.error("Unknown exact club name: " + ", ".join(sorted(missing)))
        report["selection"] = {"mode": "excerpt", "returned": len(report["clubs"])}
    print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
