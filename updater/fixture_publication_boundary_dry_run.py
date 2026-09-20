#!/usr/bin/env python3
"""Dry-run contract for fixture-level partial publication.

Reads the shadow classifier report plus the disposable candidate produced by
auto_round_results.py --publish. It never writes competition.json. The purpose
is to make the intended publication boundary explicit and machine-checkable:
fixture-local uncertainty is retained unchanged; chronology conflicts are
quarantined; only a fully regressed candidate batch may cross production.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHADOW = ROOT / "updater" / "fixture-publishability-shadow.json"
REPORT = ROOT / "updater" / "fixture-publication-boundary-dry-run.json"

def main():
    shadow = json.loads(SHADOW.read_text(encoding="utf-8"))
    counts = shadow.get("counts") or {}
    publishable = shadow.get("publishable") or []
    already = shadow.get("already_recorded") or []
    unresolved = shadow.get("unresolved") or []
    no_observation = shadow.get("no_observation") or []
    quarantined = shadow.get("quarantined") or []
    known = int(shadow.get("known_ties") or 0)

    # Every canonical tie must be accounted for exactly once. Observations can
    # include multiple source rows, so use the final decision buckets only.
    accounted = len(publishable) + len(already) + len(unresolved) + len(no_observation) + len(quarantined)
    if accounted != known:
        raise SystemExit(f"Boundary dry-run failed: {accounted} fixture decisions for {known} canonical ties.")

    # Quarantine is fixture-local: it does not erase independently publishable
    # results. The workflow's later full-candidate guards remain the global veto
    # for structural/chronology/custody/venue/Clubfinder failures.
    retained = unresolved + no_observation + quarantined
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "mode": "publication-boundary-dry-run",
        "production_write_enabled": False,
        "scan_round": shadow.get("scan_round"),
        "known_ties": known,
        "would_publish": len(publishable),
        "already_recorded": len(already),
        "would_retain_unchanged": len(retained),
        "quarantined": len(quarantined),
        "unresolved": len(unresolved),
        "no_observation": len(no_observation),
        "publishable_fixture_ids": [x.get("fixture_id") for x in publishable],
        "retained": retained,
        "contract": {
            "fixture_uncertainty_is_local": True,
            "quarantine_does_not_mutate_fixture": True,
            "global_candidate_guards_required_before_publish": True,
            "production_mutation": False,
        },
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("FIXTURE PUBLICATION BOUNDARY — DRY RUN")
    print("Production write: DISABLED")
    print("Canonical ties:", known)
    print("WOULD PUBLISH:", len(publishable))
    print("ALREADY RECORDED:", len(already))
    print("RETAIN UNCHANGED:", len(retained))
    print("  unresolved:", len(unresolved))
    print("  no observation:", len(no_observation))
    print("  quarantined:", len(quarantined))
    print("Candidate must still pass every downstream guard before publication.")

if __name__ == "__main__":
    main()
