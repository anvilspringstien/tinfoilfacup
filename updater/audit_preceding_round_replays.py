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
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

import auto_round_results as scan
from round_state_engine import classify_observation, pair_key, base_round, norm
from match_decisions import classify_batch

ROOT = Path(__file__).resolve().parents[1]
EXCEPTION_LEDGER = ROOT / "updater" / "exceptional-replay-dispositions.json"

def exceptional_dispositions():
    if not EXCEPTION_LEDGER.exists():
        return []
    payload=json.loads(EXCEPTION_LEDGER.read_text(encoding="utf-8"))
    return [x for x in (payload.get("dispositions") or [])
            if x.get("verification_state")=="human-reviewed-exception"
            and x.get("disposition")=="voided-replay-ordered"
            and x.get("disposition_source_url")]

def same_original(row, expected):
    return (
        base_round(row.get("round"))==expected.get("round")
        and str(row.get("date") or "")==str(expected.get("date") or "")
        and pair_key(row)==pair_key(expected)
        and row.get("home_score")==expected.get("home_score")
        and row.get("away_score")==expected.get("away_score")
    )

def archived_replay_source(preceding):
    """Explicit replay endpoint; base_round() deliberately strips Replay."""
    base_url = scan.fwp_round_url(preceding)
    return base_url + "-replay"


def validate_archived_replay_page(raw, preceding, url):
    marker = rf"Fixtures/Results,\s*{re.escape(scan.fwp_round_label(preceding))} Replay\s*,\s*20\d{{2}}-20\d{{2}}"
    if not re.search(marker, scan.clean(raw), re.I):
        raise SystemExit("ARCHIVED REPLAY SOURCE FAILURE: expected dedicated replay page: " + url)


ROUNDS = ["Extra Preliminary Round", "Preliminary Round", "First Round Qualifying",
          "Second Round Qualifying", "Third Round Qualifying", "Fourth Round Qualifying",
          "First Round Proper"]
UK_TZ = ZoneInfo("Europe/London")
REPLAY_COMPLETION_GRACE = timedelta(hours=4)


def reconcile_penalty_refinements(observations):
    """Treat a cross-page winner note as detail of the same level score.

    This only removes an incomplete FT observation when another page supplies
    one unambiguous penalty winner for the identical dated, oriented score.
    It is not independent penalty evidence: readiness still quarantines it.
    Different scores, dates, orientations or named winners remain conflicts.
    """
    retained, refinements = [], []
    for item in observations:
        obs = item["observation"]
        detailed = []
        if (str(obs.get("status") or "").upper().startswith("FT")
                and not obs.get("winner") and not obs.get("decision")
                and isinstance(obs.get("home_score"), int)
                and obs.get("home_score") == obs.get("away_score")
                and obs.get("date") and obs.get("source_url")):
            for other in observations:
                row = other["observation"]
                if (row.get("source_url") and row["source_url"] != obs["source_url"]
                        and row.get("date") == obs["date"]
                        and norm(row.get("home")) == norm(obs.get("home"))
                        and norm(row.get("away")) == norm(obs.get("away"))
                        and row.get("home_score") == obs["home_score"]
                        and row.get("away_score") == obs["away_score"]
                        and str(row.get("status") or "").upper().startswith("FT")
                        and row.get("decision") == "penalties"
                        and norm(row.get("winner")) in pair_key(obs)):
                    detailed.append(row)
        if detailed and len({norm(row["winner"]) for row in detailed}) == 1:
            refinements.append({"home": obs["home"], "away": obs["away"],
                                "date": obs["date"], "incomplete_source": obs["source_url"],
                                "winner_sources": sorted({row["source_url"] for row in detailed})})
        else:
            retained.append(item)
    return retained, refinements


def replay_is_due(scheduled, as_of):
    """A replay is due only after its canonical UK-local KO plus completion grace.

    Date-only fixtures become due the following local day rather than being
    treated as overdue from midnight. Missing/malformed dates still fail closed.
    """
    raw_date = scheduled.get("date")
    if not raw_date:
        return True
    try:
        fixture_date = date.fromisoformat(str(raw_date))
    except ValueError:
        return True
    if isinstance(as_of, datetime):
        now = as_of if as_of.tzinfo else as_of.replace(tzinfo=UK_TZ)
        now = now.astimezone(UK_TZ)
    else:
        now = datetime.combine(as_of, time.max, tzinfo=UK_TZ)
    raw_kickoff = str(scheduled.get("kickoff") or "").strip()
    if re.fullmatch(r"\d{1,2}:\d{2}", raw_kickoff):
        hour, minute = map(int, raw_kickoff.split(":"))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            due_at = datetime.combine(fixture_date, time(hour, minute), tzinfo=UK_TZ) + REPLAY_COMPLETION_GRACE
            return now >= due_at
    return now.date() > fixture_date


def audit(data, source_html, live_html="", source_url="", as_of=None):
    as_of = as_of or datetime.now(UK_TZ)
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
    source_observation_count = len(observations)
    observations, refinements = reconcile_penalty_refinements(observations)
    history = scan.history_rows(data)
    published_history = list(history)  # Do not mistake in-memory candidates for published results.
    known_pairs={pair_key(f) for f in known}
    exceptions=[x for x in exceptional_dispositions()
                if x.get("original",{}).get("round")==preceding
                and pair_key(x.get("original") or {}) in known_pairs]
    # Read-only overlay: the canonical file may still contain the original FT
    # result while a reviewed FA disposition awaits publication.  Reclassify
    # only the exact ledger-matched row in memory so the audit can test the
    # ordered replay without rewriting history or competition.json.
    if exceptions:
        overlaid=[]
        for row in history:
            replacement=dict(row)
            for item in exceptions:
                if same_original(row,item["original"]):
                    replacement["status"]="VOID"
                    replacement["decision"]="voided-replay-ordered"
                    replacement["winner"]=""
                    replacement["disposition_source_url"]=item["disposition_source_url"]
                    break
            overlaid.append(replacement)
        history=overlaid
    results, blocked, duplicates, events = [], [], [], []
    decisions = classify_batch(observations, history)
    for item in decisions:
        if item.get('held'):
            obs = item['observation']
            blocked.append({'home': obs['home'], 'away': obs['away'], 'date': obs['date'],
                            'reason': item['held']})
            continue
        outcome = item['outcome']
        obs = outcome.get('result') or outcome.get('event')
        kind = outcome["kind"]
        if kind == "result":
            row = outcome["result"]
            if row.get("round", "").endswith(" Replay"):
                results.append(row)
            else:
                blocked.append({"home": obs["home"], "away": obs["away"],
                                "reason": "new non-replay result in archived round"})
        elif kind == "duplicate":
            duplicates.append(outcome["result"])
        else:
            event = outcome['event']
            blocked.append({'home': event['home'], 'away': event['away'], 'date': event['date'],
                            'reason': 'replay awaiting completion: ' + event['status']})
            item.update(held=blocked[-1]['reason'], state='awaiting-decision', observation=event)
            item.pop('outcome', None)
    # Scheduled preceding-round replays are an independent completeness set.
    # A source count alone cannot prove that the source included every tie.
    observed_pairs = {pair_key(item["observation"]) for item in observations}
    candidate_pairs = {pair_key(row) for row in results + blocked}
    blocked_pairs = {pair_key(row) for row in blocked}
    recorded_pairs = {pair_key(row) for row in published_history
                      if base_round(row.get("round")) == preceding
                      and str(row.get("round") or "").endswith(" Replay")
                      and row.get("winner")}
    scheduled_replay_gaps = []
    seen_scheduled = set()
    for scheduled in (data.get("replays") or {}).values():
        if not isinstance(scheduled, dict):
            continue
        if base_round(scheduled.get("round")) != preceding:
            continue
        pair = pair_key(scheduled)
        if not all(pair) or pair in seen_scheduled:
            continue
        seen_scheduled.add(pair)
        due = replay_is_due(scheduled, as_of)
        if (pair not in recorded_pairs or pair in blocked_pairs) and (due or pair in candidate_pairs):
            scheduled_replay_gaps.append({
                "home": scheduled.get("home"), "away": scheduled.get("away"),
                "date": scheduled.get("date"),
                "source_observed": pair in observed_pairs,
                "reason": "scheduled replay lacks published terminal chronology"
            })
    # Exceptional full replays are not ordinary draw replays and therefore
    # may not exist in data["replays"] yet. Include their reviewed ledger rows
    # in the same independent completeness set.
    for item in exceptions:
        replay=item.get("replay_result") or {}
        pair=pair_key(replay)
        if not all(pair) or pair in seen_scheduled or pair in recorded_pairs:
            continue
        seen_scheduled.add(pair)
        scheduled_replay_gaps.append({
            "home": replay.get("home"), "away": replay.get("away"),
            "date": replay.get("date"),
            "source_observed": pair in observed_pairs,
            "reason": "reviewed exceptional replay lacks published terminal chronology"
        })

    return {"active_round": current, "archived_round": preceding,
            "archived_ties": len(known), "observations": len(decisions),
            "source_observations": source_observation_count,
            "penalty_refinements": refinements,
            "replay_candidates": results, "already_recorded": len(duplicates),
            "blocked": blocked, "events": len(events),
            "fixture_decisions": decisions,
            "scheduled_replay_gaps": scheduled_replay_gaps,
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
    if result['blocked']:
        import sys
        print('PRECEDING REPLAY AUDIT: fixture-local holds retained; no production changes', file=sys.stderr)


if __name__ == "__main__":
    main()
