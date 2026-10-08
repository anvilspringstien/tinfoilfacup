#!/usr/bin/env python3
"""Read-only TFFC reconciliation gate. No writes to competition data.

Usage:
  python updater/reconciliation_gate.py --production competition.json --candidate beta/competition-fallback.json
Exit 0: safe data boundary for review. Exit 1: conflicts / missing evidence.
This is a diagnostic gate, NOT permission to promote or merge.
"""
import argparse
import json
import sys
from pathlib import Path

ADVANCE = "next-round-fixture"
def rows(data, section):
    value = data.get(section, {})
    if not isinstance(value, dict):
        raise ValueError(f"{section} must be an object")
    return value

def replay_id(row):
    return (str(row.get("round", "")), tuple(sorted((str(row.get("home", "")), str(row.get("away", ""))))), str(row.get("date", "")))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--production", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    prod = json.loads(args.production.read_text(encoding="utf-8"))
    beta = json.loads(args.candidate.read_text(encoding="utf-8"))
    issues = []
    for label, data in (("production", prod), ("candidate", beta)):
        if data.get("schema_version") != 1:
            issues.append(f"{label}: unsupported schema")
        if data.get("season") != prod.get("season"):
            issues.append(f"{label}: season mismatch")
    pfix, bfix = rows(prod, "fixtures"), rows(beta, "fixtures")
    changes = {k: (pfix[k], bfix[k]) for k in pfix.keys() & bfix.keys() if pfix[k] != bfix[k]}
    missing = sorted(pfix.keys() - bfix.keys())
    if changes:
        issues.append(f"{len(changes)} existing production fixture keys differ: preserve production until separately verified")
    if missing:
        issues.append(f"{len(missing)} production fixture keys absent from candidate")
    phist, bhist = rows(prod, "result_history"), rows(beta, "result_history")
    advancement = set()
    missing_history = []
    for club, entries in phist.items():
        if not isinstance(entries, list):
            issues.append(f"production history malformed: {club}")
            continue
        candidate_entries = bhist.get(club, [])
        for entry in entries:
            if entry not in candidate_entries:
                missing_history.append(club)
                break
    if missing_history:
        issues.append(f"production history not preserved for {len(missing_history)} club keys")
    for club, entries in bhist.items():
        if not isinstance(entries, list):
            issues.append(f"candidate history malformed: {club}")
            continue
        for entry in entries:
            if isinstance(entry, dict) and entry.get("decision") == ADVANCE:
                advancement.add(replay_id(entry))
                if entry.get("home_score") is not None or entry.get("away_score") is not None:
                    issues.append(f"advancement has invented scores for {club}")
                if not entry.get("winner") or not entry.get("evidence_fixture") or not entry.get("source_url"):
                    issues.append(f"advancement lacks provenance for {club}")
    print(json.dumps({
        "status": "BLOCKED" if issues else "REVIEW_READY",
        "production_updated_at": prod.get("updated_at"),
        "candidate_updated_at": beta.get("updated_at"),
        "distinct_advancement_ties": len(advancement),
        "fixture_conflicts": len(changes),
        "production_fixture_keys_missing": len(missing),
        "production_history_keys_with_missing_entries": len(missing_history),
        "issues": issues,
        "note": "Read-only audit. REVIEW_READY is not approval to publish."
    }, indent=2))
    return 1 if issues else 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"RECONCILIATION GATE: FAIL CLOSED: {exc}", file=sys.stderr)
        sys.exit(1)
