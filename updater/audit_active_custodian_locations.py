#!/usr/bin/env python3
"""Read-only audit of current custodian ground coverage and registry lifecycle.

The competition journey controls whether a club has entered. A completed tie
venue is never silently promoted to a club's home ground, and FCHD gazetteer
candidates are only supporting evidence. This program changes NO files.
"""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ROUNDS = (
    "First Round Qualifying", "Second Round Qualifying",
    "Fourth Round Qualifying", "First Round Proper", "Third Round Proper"
)


def identity_key(value):
    """For official entrants: preserve a leading AFC (e.g. AFC Liverpool)."""
    value = str(value or "").lower().replace("&", " and ")
    value = re.sub(r"\b(association football club|football club)\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\b(fc|cfc)\b", " ", value)
    value = re.sub(r"\bafc$", " ", value)
    return " ".join(value.split())


def display_key(value):
    """Mirror the Clubfinder location lookup, not a safe identity authority."""
    value = str(value or "").lower().replace("&", " and ")
    value = re.sub(r"\b(fc|afc|cfc)\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def array_from_html(source, symbol):
    match = re.search(
        r"(?:let|const|var)\s+" + re.escape(symbol) +
        r"\s*=\s*(\[[\s\S]*?\])\s*;", source
    )
    if not match:
        raise ValueError(f"Missing {symbol} in Clubfinder HTML")
    value = json.loads(match.group(1))
    if not isinstance(value, list):
        raise ValueError(f"{symbol} is not an array")
    return value


def competition_participants(data):
    participants = set()

    def add(row):
        if not isinstance(row, dict):
            return
        if row.get("home") and row.get("away"):
            participants.add(identity_key(row["home"]))
            participants.add(identity_key(row["away"]))

    for name in ("preliminary_fixtures", "fixtures", "replays", "results"):
        for row in (data.get(name) or {}).values():
            add(row)
    for fixtures in (data.get("round_fixtures") or {}).values():
        for row in (fixtures.values() if isinstance(fixtures, dict) else fixtures):
            add(row)
    for name in (data.get("result_history") or {}):
        participants.add(identity_key(name))
    return participants


def next_round_entrants(data, round_name="Second Round Proper"):
    """Distinct fixture participants, not the tie's home-venue location."""
    clubs = {}
    for row in (data.get("fixtures") or {}).values():
        if not isinstance(row, dict) or row.get("round") != round_name:
            continue
        for side in ("home", "away"):
            name = row.get(side)
            if name:
                clubs.setdefault(display_key(name), name)
    return clubs


def analyze(root=ROOT):
    competition = json.loads((root / "competition.json").read_text("utf-8"))
    registry = json.loads((root / "journey-club-registry.json").read_text("utf-8"))
    if competition.get("season") != registry.get("season"):
        raise ValueError("Competition and registry seasons disagree")
    if len(registry.get("clubs") or []) != 252:
        raise ValueError("Expected the 252 additional journey entrants")

    builds = {}
    for name, path in (
        ("production", "clubfinder.html"),
        ("beta", "beta/clubfinder-beta.html"),
    ):
        html = (root / path).read_text("utf-8")
        eligible = array_from_html(html, "ELIGIBLE")
        records = array_from_html(html, "GROUNDS") + array_from_html(
            html, "LAW2_ORIGIN_LOCATIONS"
        )
        if len(eligible) != 651:
            raise ValueError(f"{name}: expected 651 selectable origins")
        keyed = {}
        for row in records:
            keyed.setdefault(display_key(row.get("name") or row.get("club")), []).append(row)
        builds[name] = {"eligible": eligible, "records": keyed}

    observed = competition_participants(competition)
    grouped = {}
    awaiting_now_observed = []
    for row in registry["clubs"]:
        round_name = row.get("entry_round") or "Unknown"
        counts = grouped.setdefault(round_name, {"entrants": 0, "seen": 0, "missing_location": 0})
        counts["entrants"] += 1
        active = identity_key(row["club"]) in observed
        if not active:
            continue
        counts["seen"] += 1
        if row.get("registry_state") == "awaiting-journey-entry":
            awaiting_now_observed.append(row["club"])
        if not builds["production"]["records"].get(display_key(row["club"])):
            counts["missing_location"] += 1

    next_clubs = next_round_entrants(competition)
    registry_by_name = {identity_key(x["club"]): x for x in registry["clubs"]}
    missing = {}
    for build, values in builds.items():
        missing[build] = []
        for lookup, name in sorted(next_clubs.items()):
            if lookup in values["records"]:
                continue
            record = registry_by_name.get(identity_key(name))
            candidates = (record or {}).get("supporting_ground_evidence") or []
            missing[build].append({
                "club": (record or {}).get("club") or name,
                "candidate_postcode": next(
                    (x.get("postcode") for x in candidates if x.get("type") == "fchd-gazetteer-candidate"),
                    None,
                ),
                "status": (record or {}).get("registry_state"),
            })

    # The display normaliser strips a leading AFC. Detect official identity
    # collisions, but never use such a match as an approval or promotion.
    names = [x["name"] for x in builds["production"]["eligible"]] + [
        x["club"] for x in registry["clubs"]
    ]
    identities = {}
    for name in names:
        identities.setdefault(display_key(name), set()).add(identity_key(name))
    ambiguous_keys = sorted(key for key, identities_for_key in identities.items()
                            if len(identities_for_key) > 1)
    return {
        "competition_updated_at": competition.get("updated_at"),
        "read_only": True,
        "automatic_ground_promotion": False,
        "second_round_clubs": len(next_clubs),
        "missing_second_round_custodian_locations": missing,
        "registry_entrant_coverage": grouped,
        "registry_marked_awaiting_but_seen": len(awaiting_now_observed),
        "ambiguous_display_identity_keys": ambiguous_keys,
        "safety": "Tie venues remain authoritative for ties; FCHD-only candidates are NEVER verified home grounds.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true",
                        help="Fail while any Second Round Proper custodian has no ground record")
    parser.add_argument("--require-lifecycle-current", action="store_true",
                        help="Fail if a published entrant is still labelled awaiting")
    args = parser.parse_args()
    report = analyze()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.require_lifecycle_current and report["registry_marked_awaiting_but_seen"]:
        raise SystemExit("Registry lifecycle is stale against canonical competition history")
    if args.strict and any(report["missing_second_round_custodian_locations"].values()):
        raise SystemExit("Missing ground records require independently verified review")


if __name__ == "__main__":
    main()
