#!/usr/bin/env python3
"""Read-only preceding-round replay candidate audit; never writes competition.json.

Run after active draw advances, when the normal active-round scanner can no
longer observe replays from the archived preceding round. This script reports
source observations and classifies them against archived ties and chronology.
It does NOT enable publication.
"""
import argparse
import json
import re
from pathlib import Path

import auto_round_results as scan
from round_state_engine import classify_observation, pair_key, base_round

ROOT = Path(__file__).resolve().parents[1]
def archived_replay_source(preceding):
    """Explicit replay endpoint; base_round() deliberately strips Replay."""
    base_url = scan.fwp_round_url(preceding)
    return base_url + "-replay"


def validate_archived_replay_page(raw, preceding, url):
    marker = rf"Fixtures/Results,\s*{re.escape(scan.fwp_round_label(preceding))} Replay\s*,\s*20\d{{2}}-20\d{{2}}"
    if not re.search(marker, scan.clean(raw), re.I):
        raise SystemExit("ARCHIVED REPLAY SOURCE FAILURE: expected dedicated replay page: " + url)


ROUNDS = ["Extra Preliminary Round", "Preliminary Round", "First Round Qualifying",
          "Second Round Qualifying", "Third Round Qualifying", "Fourth Round Qualifying"]


def audit(data, source_html, live_html="", source_url=""):
    current = base_round(data.get("source_round"))
    if current not in ROUNDS or ROUNDS.index(current) == 0:
        raise ValueError("no eligible preceding qualifying round")
    preceding = ROUNDS[ROUNDS.index(current) - 1]
    archived = scan.fixture_values((data.get("round_fixtures") or {}).get(preceding) or {})
    known = list({pair_key(f): dict(f, round=preceding) for f in archived}.values())
    if not known:
        raise ValueError("preceding-round archive missing; fail closed")
    observations = scan.dedupe_observations(
        scan.parse_fwp_observations(source_html, known, source_url)
        + (scan.parse_fwp_observations(live_html, known, scan.FWP_LIVE_URL) if live_html else [])
    )
    history = scan.history_rows(data)
    results, blocked, duplicates, events = [], [], [], []
    for item in observations:
        obs = item["observation"]
        # FWP can encode a penalty decision with a scoreline that disagrees
        # with the clubs' official match report (Wimborne: 3-2 vs 1-1 AET,
        # 4-3 penalties). Never silently turn that into a 90/120-minute win.
        if (str(obs.get("decision") or "").lower() == "penalties"
                and obs.get("home_score") != obs.get("away_score")):
            blocked.append({"home": obs["home"], "away": obs["away"],
                            "date": obs.get("date", ""),
                            "reason": "penalty decision with non-level source score: independent verification required"})
            continue
        try:
            outcome = classify_observation(item["fixture"], obs, history)
        except ValueError as exc:
            blocked.append({"home": obs["home"], "away": obs["away"],
                            "date": obs["date"], "reason": str(exc)})
            continue
        kind = outcome["kind"]
        if kind == "result":
            row = outcome["result"]
            if row.get("round", "").endswith(" Replay"):
                results.append(row)
                history.append(row)
            else:
                blocked.append({"home": obs["home"], "away": obs["away"],
                                "reason": "new non-replay result in archived round"})
        elif kind == "duplicate":
            duplicates.append(outcome["result"])
        else:
            events.append(outcome["event"])
    return {"active_round": current, "archived_round": preceding,
            "archived_ties": len(known), "observations": len(observations),
            "replay_candidates": results, "already_recorded": len(duplicates),
            "blocked": blocked, "events": len(events),
            "production_mutation": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-html", help="saved authoritative FWP round HTML for offline regression")
    parser.add_argument("--live-html", help="optional saved live-page HTML")
    parser.add_argument("--fetch", action="store_true", help="fetch FWP archived-round page")
    args = parser.parse_args()
    data = json.loads((ROOT / "competition.json").read_text(encoding="utf-8"))
    current = base_round(data.get("source_round"))
    if current not in ROUNDS or ROUNDS.index(current) == 0:
        raise SystemExit("PRECEDING REPLAY AUDIT: no preceding qualifying round")
    preceding = ROUNDS[ROUNDS.index(current) - 1]
    url = archived_replay_source(preceding)
    if args.fetch:
        raw = scan.fetch(url)
        validate_archived_replay_page(raw, preceding, url)
        live = scan.fetch(scan.FWP_LIVE_URL)
    elif args.source_html:
        raw = Path(args.source_html).read_text(encoding="utf-8")
        live = Path(args.live_html).read_text(encoding="utf-8") if args.live_html else ""
    else:
        parser.error("provide --fetch or --source-html")
    result = audit(data, raw, live, url)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["blocked"]:
        raise SystemExit("PRECEDING REPLAY AUDIT: blocked observations; no production changes")


if __name__ == "__main__":
    main()
