#!/usr/bin/env python3
"""Read-only fixture-level publishability shadow for guarded FA Cup results.

This deliberately does not mutate competition.json. It reuses the production
active-round parser/classifier and reports the publication decision at fixture
granularity so we can prove partial publication safely before changing the
production publication boundary.
"""
import argparse
import json
from datetime import datetime, timezone

import auto_round_results as scanner
from round_state_engine import classify_observation, pair_key

REPORT = scanner.ROOT / "updater" / "fixture-publishability-shadow.json"


def fixture_id(fixture):
    return " | ".join([
        scanner.base_round(fixture.get("round")),
        str(fixture.get("date") or ""),
        str(fixture.get("home") or ""),
        str(fixture.get("away") or ""),
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://www.thefa.com/competitions/thefacup/results")
    args = parser.parse_args()

    data = json.loads(scanner.DATA.read_text(encoding="utf-8"))
    round_name, known = scanner.active_fixtures(data)
    if not round_name or not known:
        raise SystemExit("Publishability shadow health failure: no canonical active draw available.")

    source_url = scanner.fwp_round_url(round_name)
    primary_raw = scanner.fetch(args.url)
    fixtures_raw = scanner.fetch(source_url)
    scanner.validate_fwp_round_page(fixtures_raw, round_name, source_url)
    live_raw = scanner.fetch(scanner.FWP_LIVE_URL)

    by_source = {
        "primary_awards": scanner.parse_primary_awards(primary_raw, known, args.url),
        "fwp_fixtures": scanner.parse_fwp_observations(fixtures_raw, known, source_url),
        "fwp_live": scanner.parse_fwp_observations(live_raw, known, scanner.FWP_LIVE_URL),
    }
    observations = scanner.dedupe_observations(sum(by_source.values(), []))
    history = scanner.history_rows(data)

    observed_pairs = set()
    decisions = []
    publishable = []
    already_recorded = []
    unresolved = []
    quarantined = []

    for item in observations:
        fixture, observation = item["fixture"], item["observation"]
        observed_pairs.add(pair_key(fixture))
        base = {
            "fixture_id": fixture_id(fixture),
            "round": round_name,
            "home": fixture.get("home"),
            "away": fixture.get("away"),
            "fixture_date": fixture.get("date", ""),
            "observation_date": observation.get("date", ""),
            "source_url": observation.get("source_url", ""),
        }
        try:
            outcome = classify_observation(fixture, observation, history)
        except ValueError as exc:
            row = {**base, "decision": "quarantine", "reason": str(exc)}
            quarantined.append(row)
            decisions.append(row)
            continue

        kind = outcome["kind"]
        if kind == "result":
            result = outcome["result"]
            row = {
                **base,
                "decision": "publishable",
                "reason": outcome.get("reason", ""),
                "result": {
                    "home": result.get("home"),
                    "away": result.get("away"),
                    "home_score": result.get("home_score"),
                    "away_score": result.get("away_score"),
                    "winner": result.get("winner", ""),
                    "round": result.get("round", ""),
                    "date": result.get("date", ""),
                    "status": result.get("status", ""),
                    "decision": result.get("decision", ""),
                },
            }
            publishable.append(row)
            decisions.append(row)
            history.append(result)
            history = scanner.unique_history(history)
        elif kind == "duplicate":
            row = {**base, "decision": "already-recorded", "reason": outcome.get("reason", "")}
            already_recorded.append(row)
            decisions.append(row)
        else:
            event = outcome.get("event") or {}
            row = {
                **base,
                "decision": "unresolved",
                "reason": outcome.get("reason", ""),
                "status": event.get("status", ""),
            }
            unresolved.append(row)
            decisions.append(row)

    no_observation = []
    for fixture in known:
        if pair_key(fixture) not in observed_pairs:
            no_observation.append({
                "fixture_id": fixture_id(fixture),
                "round": round_name,
                "home": fixture.get("home"),
                "away": fixture.get("away"),
                "fixture_date": fixture.get("date", ""),
                "decision": "no-observation",
                "reason": "No current source observation mapped to this canonical tie.",
            })

    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "mode": "read-only-shadow",
        "production_mutation": False,
        "scan_round": round_name,
        "known_ties": len(known),
        "source_observations": {name: len(rows) for name, rows in by_source.items()},
        "semantic_observations": len(observations),
        "counts": {
            "publishable": len(publishable),
            "already_recorded": len(already_recorded),
            "unresolved": len(unresolved),
            "quarantined": len(quarantined),
            "no_observation": len(no_observation),
        },
        "publishable": publishable,
        "already_recorded": already_recorded,
        "unresolved": unresolved,
        "quarantined": quarantined,
        "no_observation": no_observation,
        "decisions": decisions,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("FIXTURE PUBLISHABILITY SHADOW")
    print("Mode: READ ONLY — competition.json unchanged")
    print("Active round:", round_name)
    print("Canonical ties:", len(known))
    print("Semantic observations:", len(observations))
    for key, value in report["counts"].items():
        print(key.replace("_", " ").title() + ":", value)

    if quarantined:
        print("QUARANTINED:", len(quarantined), "fixture observation(s); production remains untouched.")


if __name__ == "__main__":
    main()
