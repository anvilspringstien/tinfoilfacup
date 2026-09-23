#!/usr/bin/env python3
"""Read-only publication readiness gate for archived replay candidates.

Never writes competition.json. A single source's penalty decision is not
independent corroboration, even when its scoreline has been corrected.
"""
import argparse
import json
from pathlib import Path
from reconcile_quarantined_replay_evidence import reconcile

EXPECTED_REPLAYS = 13


def readiness(report, evidence_by_fixture=None):
    evidence_by_fixture = evidence_by_fixture or {}
    if report.get("production_mutation") is not False:
        raise ValueError("audit must explicitly be read-only")
    candidates = report.get("replay_candidates", [])
    blocked = report.get("blocked", [])
    if len(candidates) + len(blocked) != EXPECTED_REPLAYS:
        raise ValueError("all 13 archived replay fixtures must be accounted for")
    seen = set()
    approved, held = [], []
    for row in candidates:
        key = "|".join((row["date"], *sorted((row["home"].casefold(), row["away"].casefold()))))
        if key in seen:
            raise ValueError("duplicate replay candidate")
        seen.add(key)
        if row.get("round") != "Second Round Qualifying Replay" or not row.get("winner"):
            raise ValueError("undecided or wrong-round replay candidate")
        if row.get("decision") == "penalties":
            fixture = {"home": row["home"], "away": row["away"],
                       "date": row["date"],
                       "reason": "penalty decision with non-level source score: independent verification required"}
            verdict = reconcile(fixture, evidence_by_fixture.get(key, []))
            if verdict["status"] != "independently_verified":
                held.append({"fixture": key, "reason": "two independent penalty reports required"})
                continue
            confirmed = verdict["result"]
            if any(confirmed[k] != row[k] for k in ("winner", "home_score", "away_score", "date")):
                held.append({"fixture": key, "reason": "independent evidence conflicts with staged result"})
                continue
        approved.append(row)
    for row in blocked:
        key = "|".join((row.get("date", ""), *sorted((row["home"].casefold(), row["away"].casefold()))))
        if key in seen:
            raise ValueError("blocked fixture also staged")
        seen.add(key)
        held.append({"fixture": key, "reason": row.get("reason", "blocked by source audit")})
    if len(seen) != EXPECTED_REPLAYS:
        raise ValueError("replay fixture identities are not unique")
    return {"status": "ready" if not held else "partial_ready",
            "approved_count": len(approved), "held_count": len(held),
            "approved": approved, "held": held, "production_mutation": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, help="source-attributed independent penalty reports")
    args = parser.parse_args()
    report = json.loads(args.audit.read_text(encoding="utf-8"))
    evidence = json.loads(args.evidence.read_text(encoding="utf-8")) if args.evidence else {}
    print(json.dumps(readiness(report, evidence), indent=2))


if __name__ == "__main__":
    main()
