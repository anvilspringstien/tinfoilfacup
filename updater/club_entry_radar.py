#!/usr/bin/env python3
"""Read-only, round-aware entrant/home-ground radar for Mission Control.

Canonical competition.json determines participation and round membership.
Clubfinder ground registries supply evidence only; neither those registries
nor fixture venues may be changed or treated as proof of a home ground.
Writes nothing unless the caller explicitly redirects stdout.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

from updater.audit_active_custodian_locations import (
    ROOT, array_from_html, display_key, identity_key,
)

ROUND_ORDER = (
    "Extra Preliminary Round", "Preliminary Round",
    "First Round Qualifying", "Second Round Qualifying",
    "Third Round Qualifying", "Fourth Round Qualifying",
    "First Round Proper", "Second Round Proper",
    "Third Round Proper", "Fourth Round Proper",
    "Fifth Round Proper", "Quarter Final", "Semi Final", "Final",
)


def round_fixtures(competition):
    """Extract canonical round/participant pairs from fixture and result data.

    A round must be explicit on a tie or supplied by the round_fixtures bucket.
    Historical result key names and tie venues are never home-ground evidence.
    """
    collected = defaultdict(dict)
    sources = ("preliminary_fixtures", "fixtures", "replays", "results")
    for source in sources:
        rows = competition.get(source) or {}
        if not isinstance(rows, dict):
            raise ValueError(f"Malformed canonical {source}")
        for tie in rows.values():
            if not isinstance(tie, dict):
                continue
            round_name = tie.get("round")
            if not round_name:
                continue
            _add_tie(collected, round_name, tie)
    buckets = competition.get("round_fixtures") or {}
    if not isinstance(buckets, dict):
        raise ValueError("Malformed canonical round_fixtures")
    for round_name, rows in buckets.items():
        if not isinstance(rows, (dict, list)):
            raise ValueError(f"Malformed round bucket: {round_name}")
        for tie in (rows.values() if isinstance(rows, dict) else rows):
            if isinstance(tie, dict):
                explicit = tie.get("round")
                if explicit and explicit != round_name:
                    raise ValueError(f"Conflicting round labels: {round_name} / {explicit}")
                _add_tie(collected, round_name, tie)
    return collected


def _add_tie(collected, round_name, tie):
    if not isinstance(round_name, str) or not round_name.strip():
        raise ValueError("Missing round name")
    home, away = tie.get("home"), tie.get("away")
    if not home or not away:
        return
    for club in (home, away):
        key = identity_key(club)
        if not key:
            raise ValueError("Empty entrant identity")
        collected[round_name].setdefault(key, club)


def _ground_registry(html):
    records = array_from_html(html, "GROUNDS") + array_from_html(
        html, "LAW2_ORIGIN_LOCATIONS")
    lookup = defaultdict(list)
    for record in records:
        name = record.get("name") or record.get("club")
        if name:
            lookup[display_key(name)].append(record)
    return lookup


def inspect_rounds(competition, registries, journey_registry=None):
    """Pure inspection function, suitable for synthetic regression fixtures."""
    if not isinstance(competition, dict):
        raise ValueError("Invalid canonical competition")
    rounds = round_fixtures(competition)
    registry = {}
    if journey_registry:
        if competition.get("season") != journey_registry.get("season"):
            raise ValueError("Competition/registry season mismatch")
        for row in journey_registry.get("clubs", []):
            key = identity_key(row.get("club"))
            if key in registry:
                raise ValueError("Duplicate journey registry identity")
            registry[key] = row
    sources = {name: _ground_registry(html) for name, html in registries.items()}
    names = sorted(rounds, key=lambda r: (
        ROUND_ORDER.index(r) if r in ROUND_ORDER else len(ROUND_ORDER), r))
    previously_seen = set()
    reports = []
    for round_name in names:
        entrants = rounds[round_name]
        clubs = []
        for key, name in sorted(entrants.items(), key=lambda item: item[1].casefold()):
            row = {"club": name, "identity": key,
                   "new_to_observed_rounds": key not in previously_seen,
                   "sources": {}}
            candidate = registry.get(key)
            if candidate:
                row["registry_state"] = candidate.get("registry_state")
                row["entry_round"] = candidate.get("entry_round")
            for source_name, known in sources.items():
                possible = known.get(display_key(name), [])
                exact = [record for record in possible
                         if identity_key(record.get("name") or record.get("club")) == key]
                if len(exact) > 1 or (possible and len(exact) != 1):
                    status, record = "identity_conflict", None
                elif not exact:
                    status, record = "missing_ground", None
                else:
                    record = exact[0]
                    if not record.get("ground") or not record.get("postcode"):
                        status = "missing_ground"
                    elif record.get("verification") == "verified":
                        status = "verified_location"
                    else:
                        status = "ground_recorded_coordinates_pending"
                info = {"status": status}
                if record:
                    info.update({"ground": record.get("ground"),
                                 "postcode": record.get("postcode"),
                                 "verification": record.get("verification"),
                                 "official_source": record.get("source")})
                row["sources"][source_name] = info
            clubs.append(row)
        totals = {}
        for source_name in sources:
            totals[source_name] = {
                status: sum(c["sources"][source_name]["status"] == status for c in clubs)
                for status in ("verified_location", "ground_recorded_coordinates_pending",
                               "missing_ground", "identity_conflict")
            }
        reports.append({"round": round_name, "entrant_count": len(clubs),
                        "new_to_observed_rounds": sum(c["new_to_observed_rounds"] for c in clubs),
                        "coverage": totals, "clubs": clubs})
        previously_seen.update(entrants)
    return {"schema_version": 1, "read_only": True,
            "canonical_source": "competition.json",
            "season": competition.get("season"),
            "competition_updated_at": competition.get("updated_at"),
            "automatic_ground_promotion": False,
            "fixture_venues_used_as_home_grounds": False,
            "rounds": reports}


def analyze(root=ROOT):
    root = Path(root)
    competition = json.loads((root / "competition.json").read_text("utf-8"))
    journey = json.loads((root / "journey-club-registry.json").read_text("utf-8"))
    sources = {
        "production": (root / "clubfinder.html").read_text("utf-8"),
        "beta": (root / "beta/clubfinder-beta.html").read_text("utf-8"),
    }
    return inspect_rounds(competition, sources, journey)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true",
                        help="Fail if any observed round has missing or conflicting grounds")
    args = parser.parse_args()
    report = analyze()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.strict and any(
        count for r in report["rounds"] for source in r["coverage"].values()
        for status, count in source.items()
        if status in ("missing_ground", "identity_conflict")
    ):
        raise SystemExit("Club Entry Radar: missing/conflicting ground records")


if __name__ == "__main__":
    main()
