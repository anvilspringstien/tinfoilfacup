#!/usr/bin/env python3
"""Read-only publication readiness gate for archived replay candidates.

Never writes competition.json. A single source's penalty decision is not
independent corroboration, even when its scoreline has been corrected.
"""
import argparse
import json
from pathlib import Path
from reconcile_quarantined_replay_evidence import reconcile
from round_state_engine import pair_key


def readiness(report, evidence_by_fixture=None):
    """Approve only unpublished scheduled replays covered by the live source.

    Already-recorded ties count towards source accounting but must never be
    re-staged. Each scheduled gap needs its own observed candidate or hold;
    a coincidentally correct observation count is not completeness evidence.
    """
    evidence_by_fixture = evidence_by_fixture or {}
    if report.get("production_mutation") is not False:
        raise ValueError("audit must explicitly be read-only")
    candidates = report.get("replay_candidates", [])
    blocked = report.get("blocked", [])
    gaps = report.get("scheduled_replay_gaps")
    recorded = report.get("already_recorded")
    observations = report.get("observations")
    if not isinstance(gaps, list) or not isinstance(recorded, int) or not isinstance(observations, int):
        raise ValueError("audit must supply scheduled gaps, recorded and observed counts")
    if recorded < 0 or observations < 0 or report.get("events"):
        raise ValueError("incomplete or nonterminal replay observations")
    if len(candidates) + len(blocked) + recorded != observations:
        raise ValueError("source observations are not fully accounted for")

    def identity(row):
        key = pair_key(row)
        if len(key) != 2 or not row.get("date"):
            raise ValueError("incomplete replay fixture identity")
        return row["date"], key

    expected = {}
    for gap in gaps:
        key = identity(gap)
        if key in expected:
            raise ValueError("duplicate scheduled replay gap")
        if gap.get("source_observed") is not True:
            raise ValueError("scheduled replay absent from source")
        expected[key] = gap

    seen = set()
    approved, held = [], []
    for row in candidates:
        key = identity(row)
        if key not in expected or key in seen:
            raise ValueError("unmatched or duplicate replay candidate")
        seen.add(key)
        if row.get("round") != "Second Round Qualifying Replay" or not row.get("winner"):
            raise ValueError("undecided or wrong-round replay candidate")
        if row.get("decision") == "penalties":
            fixture = {"home": row["home"], "away": row["away"],
                       "date": row["date"],
                       "reason": "penalty decision with non-level source score: independent verification required"}
            evidence_key = "|".join((row["date"], *sorted((row["home"].casefold(), row["away"].casefold()))))
            verdict = reconcile(fixture, evidence_by_fixture.get(evidence_key, []))
            if verdict["status"] != "independently_verified":
                held.append({"fixture": evidence_key, "reason": "two independent penalty reports required"})
                continue
            confirmed = verdict["result"]
            if any(confirmed[k] != row[k] for k in ("winner", "home_score", "away_score", "date")):
                held.append({"fixture": evidence_key, "reason": "independent evidence conflicts with staged result"})
                continue
        approved.append(row)

    for row in blocked:
        key = identity(row)
        if key not in expected or key in seen:
            raise ValueError("unmatched or duplicate blocked replay")
        seen.add(key)
        evidence_key = "|".join((row["date"], *sorted((row["home"].casefold(), row["away"].casefold()))))
        held.append({"fixture": evidence_key, "reason": row.get("reason", "blocked by source audit")})
    if seen != set(expected):
        raise ValueError("scheduled replay has no source-backed result or quarantine")
    return {"status": "ready" if not held else "partial_ready",
            "approved_count": len(approved), "held_count": len(held),
            "already_recorded": recorded, "observations": observations,
            "scheduled_replay_gaps": gaps,
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
