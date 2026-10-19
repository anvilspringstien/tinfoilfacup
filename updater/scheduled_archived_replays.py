"""Connect ordinary archived replays to scheduled Results' existing publish guards.

Source audit, per-fixture readiness and in-memory staging are shared with the
manual recovery route. No direct writes or exceptional evidence overrides.
"""
import copy

import audit_preceding_round_replays as audit
import auto_round_results as scan
from guard_archived_replay_promotion import readiness
from stage_preceding_replay_candidates import stage
from sync_active_replay_fixtures import unresolved_draws
from round_state_engine import base_round, is_draw


def collect(data, fetch, live_html="", as_of=None):
    current = base_round(data.get("source_round"))
    if current not in audit.ROUNDS or audit.ROUNDS.index(current) == 0:
        return data, {"status": "not-applicable", "changed": False}, None
    preceding = audit.ROUNDS[audit.ROUNDS.index(current) - 1]
    pending = [r for r in unresolved_draws(data) if base_round(r.get("round")) == preceding]
    if not pending:
        candidate, resolutions = resolve_conditionals(data, preceding)
        return candidate, {"status": "no-outstanding-replays", "changed": candidate != data,
                           "resolutions": resolutions}, None
    import auto_draw as draw
    original_fixtures = draw.fixture_values((data.get("round_fixtures") or {}).get(preceding) or {})
    scheduled = draw.fixture_values(data.get("replays") or {})
    for original in pending:
        matches = [f for f in original_fixtures if f.get("date") == original.get("date")
                   and scan.match_fixture([f], original.get("home"), original.get("away"))]
        if len(matches) != 1 or not original.get("source_url"):
            raise ValueError("Pending replay lacks unique sourced archived original")
        replay_matches = [r for r in scheduled if r.get("round") == preceding + " Replay"
                          and r.get("source_url") and r.get("date", "") > original.get("date", "")
                          and scan.match_fixture([matches[0]], r.get("home"), r.get("away"))]
        if len(replay_matches) != 1:
            raise ValueError("Pending replay lacks unique canonical schedule")
    url = audit.archived_replay_source(preceding)
    raw = fetch(url)
    audit.validate_archived_replay_page(raw, preceding, url)
    report = audit.audit(data, raw, live_html, url, as_of=as_of)
    gate = readiness(report)
    # Retain the recovery route's independent penalty-evidence requirement.
    # Held fixtures stay unresolved; independently cleared fixtures may advance.
    if not gate["approved"]:
        return data, {"status": "evidence-held" if gate["held"] else "awaiting-replays",
                      "changed": False, "audit": report, "held": gate["held"]}, {"url": url, "html": raw}
    summary, candidate = stage(data, dict(report, replay_candidates=gate["approved"], blocked=[]))
    candidate, resolutions = resolve_conditionals(candidate, preceding)
    return candidate, {"status": "partial-ready" if gate["held"] else "staged",
                       "held": gate["held"], "changed": candidate != data,
                       "audit": report, "staged": summary, "resolutions": resolutions}, {"url": url, "html": raw}


def resolve_conditionals(data, preceding):
    """Resolve only a whole two-club placeholder with unique replay ancestry.

    Current-round dates, venues and other fields survive unchanged. The played
    original and replay retain their own metadata in results/history/archive.
    """
    import auto_draw as draw
    current = draw.fixture_values(data.get("fixtures") or {})
    if not any(draw.is_conditional_fixture(f) for f in current):
        return data, []
    history = scan.history_rows(data)
    originals = draw.fixture_values((data.get("round_fixtures") or {}).get(preceding) or {})
    changed = []
    output = []
    for fixture in current:
        updated = copy.deepcopy(fixture)
        for side in ("home", "away"):
            options = draw.alternatives(fixture.get(side, ""))
            if len(options) < 2:
                continue
            if len(options) != 2:
                raise ValueError("Unsupported conditional participant count")
            def matches(row):
                return ((draw.compatible(options[0], row.get("home")) and draw.compatible(options[1], row.get("away"))) or
                        (draw.compatible(options[1], row.get("home")) and draw.compatible(options[0], row.get("away"))))
            archived = [r for r in originals if matches(r)]
            if len(archived) != 1:
                raise ValueError("Conditional slot lacks unique archived original")
            original = archived[0]
            draws = [r for r in history if r.get("round") == preceding and matches(r)
                     and r.get("date") == original.get("date") and r.get("source_url")
                     and is_draw(r)]
            if len(draws) != 1:
                raise ValueError("Conditional slot lacks unique sourced drawn original")
            replays = [r for r in history if r.get("round") == preceding + " Replay" and matches(r)
                       and r.get("date", "") > original.get("date", "") and r.get("source_url") and r.get("winner")]
            if not replays:
                continue
            # Reclassify against original ancestry to reject conflicting outcomes.
            for result in replays:
                scan.classify_observation(original, result, draws)
            winners = {draw.norm(r["winner"]) for r in replays}
            if len(winners) != 1:
                raise ValueError("Conflicting replay winners for conditional slot")
            winners_in_slot = [o for o in options if draw.compatible(o, replays[0]["winner"])]
            if len(winners_in_slot) != 1:
                raise ValueError("Replay winner is ambiguous in conditional slot")
            updated[side] = winners_in_slot[0]
            changed.append({"from": fixture[side], "to": updated[side], "side": side})
        if not draw.is_conditional_fixture(updated):
            updated.pop("conditional", None)
        output.append(updated)
    if changed:
        data = copy.deepcopy(data)
        data["fixtures"] = draw.fixture_map(output)
    return data, changed
