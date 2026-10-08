#!/usr/bin/env python3
"""Read-only shadow producer: propose scoreless replay advancements from canonical draws.

This never publishes or edits competition.json. A definite official next-round
fixture is evidence of advancement, not evidence of the replay score.
"""
import argparse
import json
from pathlib import Path

from build_reconciliation_candidate import build, match

def rows(value):
    return list(value.values()) if isinstance(value, dict) else list(value or [])

def propose(data):
    source = str(data.get("source_url") or "")
    if not source.startswith("https://www.thefa.com/"):
        return [], ["canonical draw source is not an official FA URL"]
    fixtures = rows(data.get("fixtures"))
    replays = rows(data.get("replays"))
    evidence = []
    blocked = []
    for replay in replays:
        if not isinstance(replay, dict) or not str(replay.get("round") or "").lower().endswith(" replay"):
            continue
        key = match(replay)
        if len(key) != 2 or not all(key) or not replay.get("date"):
            blocked.append("malformed replay identity")
            continue
        # Only a unique, definite canonical fixture may establish advancement.
        matches = [f for f in fixtures if isinstance(f, dict) and
                   len(set(key) & set(match(f))) == 1 and
                   not f.get("conditional") and
                   " or " not in str(f.get("home", "")).lower() and
                   " or " not in str(f.get("away", "")).lower()]
        distinct = {(match(f), f.get("round"), f.get("date")): f for f in matches}
        if not distinct:
            continue  # No evidence: never guess a winner.
        if len(distinct) != 1:
            blocked.append(f"ambiguous next-round evidence: {key}")
            continue
        fixture = next(iter(distinct.values()))
        winner = next(iter(set(key) & set(match(fixture))))
        winner_name = replay["home"] if replay["home"].strip().lower() == winner else replay["away"]
        evidence.append({
            "round": replay["round"], "home": replay["home"], "away": replay["away"],
            "date": replay["date"], "home_score": None, "away_score": None,
            "winner": winner_name, "decision": "next-round-fixture",
            "status": "ADVANCEMENT_CONFIRMED", "source_url": source,
            "evidence_round": fixture["round"],
            "evidence_fixture": f'{fixture["home"]} v {fixture["away"]}',
        })
    return evidence, blocked

def shadow(data):
    proposals, blocked = propose(data)
    # Use the existing production-first builder and its conflict protections.
    evidence = {"schema_version": data.get("schema_version"), "season": data.get("season"),
                "result_history": {}}
    for row in proposals:
        for club in (row["home"], row["away"]):
            evidence["result_history"].setdefault(club, []).append(row)
    candidate, imported, issues = build(data, evidence)
    return {"status": "BLOCKED" if blocked or issues else "SHADOW_OK",
            "proposed": len(proposals), "accepted": len(imported),
            "issues": blocked + issues}, candidate

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--competition", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    data = json.loads(args.competition.read_text(encoding="utf-8"))
    report, _ = shadow(data)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if report["status"] == "BLOCKED" else 0

if __name__ == "__main__":
    raise SystemExit(main())
