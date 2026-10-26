#!/usr/bin/env python3
"""Fixture-local promotion preview for archived qualifying replays.

Never writes competition.json. Reuses the audited source classification and the
production merge function on a deep copy to expose precisely what would change.
Blocked observations stay quarantined; healthy candidates remain independently
inspectable. No automatic production promotion is enabled.
"""
import argparse
import copy
import json
from pathlib import Path

import audit_preceding_round_replays as audit
import auto_round_results as scan
from round_state_engine import pair_key

ROOT = Path(__file__).resolve().parents[1]


def preview(data, source_html, live_html="", source_url=""):
    report = audit.audit(data, source_html, live_html, source_url)
    candidate = copy.deepcopy(data)
    accepted, quarantined = [], list(report["blocked"])
    seen = set()
    for row in report["replay_candidates"]:
        key = (tuple(sorted(pair_key(row))), row.get("date"), row.get("round"))
        if key in seen:
            quarantined.append({"home": row["home"], "away": row["away"],
                                "reason": "duplicate candidate for same tie and date"})
            continue
        seen.add(key)
        if row.get("round") != report["archived_round"] + " Replay":
            quarantined.append({"home": row["home"], "away": row["away"],
                                "reason": "candidate is not an archived-round replay"})
            continue
        if not row.get("winner"):
            quarantined.append({"home": row["home"], "away": row["away"],
                                "reason": "no decisive replay winner"})
            continue
        if scan.merge_result(candidate, row):
            accepted.append(row)
    return {
        "mode": "read-only-promotion-preview",
        "production_mutation": False,
        "archived_round": report["archived_round"],
        "source_observations": report["observations"],
        "already_recorded": len(report["already_recorded"]),
        "publishable": accepted,
        "quarantined": quarantined,
        "candidate_data": candidate,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fetch", action="store_true")
    p.add_argument("--source-html")
    p.add_argument("--live-html")
    p.add_argument("--report", default="/tmp/preceding-replay-promotion-preview.json")
    args = p.parse_args()
    data = json.loads((ROOT / "competition.json").read_text(encoding="utf-8"))
    preceding = audit.ROUNDS[audit.ROUNDS.index(
        scan.base_round(data["source_round"])) - 1]
    url = scan.fwp_round_url(preceding)
    if args.fetch:
        source = scan.fetch(url)
        scan.validate_fwp_round_page(source, preceding, url)
        live = scan.fetch(scan.FWP_LIVE_URL)
    elif args.source_html:
        source = Path(args.source_html).read_text(encoding="utf-8")
        live = Path(args.live_html).read_text(encoding="utf-8") if args.live_html else ""
    else:
        p.error("provide --fetch or --source-html")
    result = preview(data, source, live, url)
    # Candidate data is a simulation, never written to competition.json.
    result.pop("candidate_data")
    Path(args.report).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["quarantined"]:
        print("Quarantined observations require independent resolution; no publication.")


if __name__ == "__main__":
    main()
