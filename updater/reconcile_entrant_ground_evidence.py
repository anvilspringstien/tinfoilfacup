#!/usr/bin/env python3
"""Read-only Construction Law reconciliation: staged evidence vs live entrant gaps.

No files are modified. Neither an FCHD candidate nor a fixture's away venue
counts as verified home-ground evidence.
"""
import json
from pathlib import Path
from updater.audit_active_custodian_locations import analyze, identity_key

ROOT = Path(__file__).resolve().parents[1]


def reconcile(root=ROOT):
    evidence = json.loads((root / "updater/entrant-home-ground-evidence-2026.json").read_text(encoding="utf-8"))
    audit = analyze(root)
    rows = evidence["clubs"]
    by_key = {}
    for row in rows:
        key = identity_key(row["official_identity"])
        if not key or key in by_key:
            raise ValueError("Duplicate or empty official evidence identity: " + row["official_identity"])
        if row.get("review_status") not in (
            "awaiting-coordinates-and-human-promotion", "awaiting-human-promotion"
        ):
            raise ValueError("Evidence row improperly authorised for promotion: " + row["official_identity"])
        by_key[key] = row
    blocked = {identity_key(x["official_identity"]) for x in evidence.get("unresolved_conflicts", [])}
    if blocked.intersection(by_key):
        raise ValueError("Blocked identity appears in approved evidence pool")
    missing = audit["missing_second_round_custodian_locations"]
    result = {}
    for build in ("production", "beta"):
        gap_names = {identity_key(r["club"]) for r in missing[build]}
        staged = sorted(row["official_identity"] for k, row in by_key.items() if k in gap_names)
        result[build] = {
            "missing_location_count": len(gap_names),
            "evidence_staged_for_missing": staged,
            "missing_without_staged_evidence": sorted(
                r["club"] for r in missing[build] if identity_key(r["club"]) not in by_key
            ),
        }
    return {
        "read_only": True,
        "automatic_ground_promotion": False,
        "staged_evidence_count": len(rows),
        "blocked_conflict_count": len(blocked),
        "second_round_clubs": audit["second_round_clubs"],
        "builds": result,
    }


if __name__ == "__main__":
    print(json.dumps(reconcile(), indent=2, ensure_ascii=False))
