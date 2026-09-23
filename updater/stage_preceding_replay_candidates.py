#!/usr/bin/env python3
"""Stage archived replay candidates in memory; never publish production data."""
import argparse
import copy
import json
from pathlib import Path

import audit_preceding_round_replays as audit
import auto_round_results as scan
from round_state_engine import norm, compatible, base_round, pair_key

ROOT = Path(__file__).resolve().parents[1]
DRAW_ALIASES = {
    "hamp and rich": "hampton and richmond borough",
    "weston sm": "weston super mare",
    "cray wands": "cray wanderers",
    "dag and red": "dagenham and redbridge",
    "win finch": "wingate and finchley",
    "g borough t": "gainsborough trinity",
}


def draw_matches(data, winner):
    matches = {}
    for fixture in scan.fixture_values(data.get("fixtures") or {}):
        sides = [p.strip() for side in (fixture["home"], fixture["away"])
                 for p in side.split(" or ")]
        if any(compatible(DRAW_ALIASES.get(norm(side), side), winner) for side in sides):
            key = (fixture["home"], fixture["away"], fixture.get("date"))
            matches[key] = fixture
    return list(matches.values())


def stage(data, report):
    if report.get("production_mutation") is not False:
        raise ValueError("audit must be read-only")
    blocked = report["blocked"]
    if any(not ("Wimborne" in b.get("home", "") or "Wimborne" in b.get("away", ""))
           or "penalty decision with non-level source score" not in b.get("reason", "")
           for b in blocked):
        raise ValueError("unexpected source conflict: fail closed")
    staged = copy.deepcopy(data)
    history = scan.history_rows(staged)
    staged_rows = []
    for result in report["replay_candidates"]:
        if not result.get("round", "").endswith(" Replay") or not result.get("winner"):
            raise ValueError("candidate is not a decided replay")
        originals = [r for r in history
                     if pair_key(r) == pair_key(result)
                     and base_round(r.get("round")) == base_round(result.get("round"))
                     and not r.get("round", "").endswith(" Replay")
                     and r.get("decision") == "draw-replay"
                     and r.get("date", "") < result.get("date", "")]
        if len(originals) != 1:
            raise ValueError("replay original not uniquely verified")
        destinations = draw_matches(data, result["winner"])
        if len(destinations) != 1:
            raise ValueError("replay winner has no unique next-round draw: " + result["winner"])
        if not scan.merge_result(staged, result):
            raise ValueError("unexpected duplicate replay candidate")
        staged_rows.append({"winner": result["winner"],
                            "replay": result["home"] + " v " + result["away"],
                            "next_fixture": destinations[0]["home"] + " v " + destinations[0]["away"]})
    if data == staged:
        raise ValueError("no staged changes")
    return {"staged_count": len(staged_rows), "quarantined": blocked,
            "staged": staged_rows, "production_mutation": False}, staged


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate-output', type=Path, help='Write candidate ONLY to an isolated non-repository path')
    args = parser.parse_args()
    if args.candidate_output:
        destination = args.candidate_output.resolve()
        if ROOT.resolve() == destination or ROOT.resolve() in destination.parents:
            raise SystemExit('Candidate output must be outside the repository')
    data = json.loads((ROOT / "competition.json").read_text(encoding="utf-8"))
    current = base_round(data.get("source_round"))
    if current not in audit.ROUNDS or audit.ROUNDS.index(current) == 0:
        raise SystemExit("No eligible archived round")
    previous = audit.ROUNDS[audit.ROUNDS.index(current)-1]
    url = audit.archived_replay_source(previous)
    raw = scan.fetch(url)
    audit.validate_archived_replay_page(raw, previous, url)
    live = scan.fetch(scan.FWP_LIVE_URL)
    report = audit.audit(data, raw, live, url)
    if not report["replay_candidates"]:
        diagnostics = {"status": "no_replay_candidates", "archived_ties": report["archived_ties"],
                       "observations": report["observations"], "already_recorded": report["already_recorded"],
                       "blocked": report["blocked"], "events": report["events"],
                       "source_url": url, "production_mutation": False}
        print(json.dumps(diagnostics, indent=2))
        raise SystemExit("No replay candidates in current source: inspect observation counts and archived source; publication withheld")
    summary, candidate = stage(data, report)
    if args.candidate_output:
        args.candidate_output.write_text(json.dumps(candidate, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    # Deliberately no --publish mode or write to competition.json.


if __name__ == "__main__":
    main()
