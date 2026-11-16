"""Recover unfinished fixtures and durable holds after the draw has advanced."""
import copy
from collections import defaultdict
from datetime import datetime, timezone

from match_decisions import classify_batch, retain_holds
from round_state_engine import base_round, pair_key, is_draw


def retry_archived_holds(data, fetch, live_html='', visited_rounds=()):
    import auto_round_results as scan
    import auto_draw as draw
    import audit_preceding_round_replays as audit
    current = base_round(data.get('source_round'))
    visited = set(visited_rounds) | {current}
    pending = [h for h in data.get('pending_match_decisions', [])
               if base_round(h['fixture'].get('round')) not in visited]
    if not pending:
        return data, {'changed': False, 'retried': 0, 'recovered': 0, 'source_failures': []}
    candidate = copy.deepcopy(data)
    cache, failures, recovered = {}, [], []
    for hold in pending:
        fixture = hold['fixture']
        rnd = base_round(fixture.get('round'))
        originals = draw.fixture_values((data.get('round_fixtures') or {}).get(rnd) or {})
        backed = [f for f in originals if f.get('date') == fixture.get('date')
                  and ((draw.compatible(f['home'], fixture['home']) and draw.compatible(f['away'], fixture['away']))
                       or (draw.compatible(f['away'], fixture['home']) and draw.compatible(f['home'], fixture['away'])))]
        if len(backed) != 1:
            raise ValueError('pending decision lacks unique canonical archived fixture')
        replay = rnd in scan.FWP_ROUND_SLUGS and any(
            pair_key(r) == pair_key(fixture) and base_round(r.get('round')) == rnd
            and str(r.get('date') or '') < hold['date']
            and (is_draw(r) or r.get('decision') == 'voided-replay-ordered')
            for r in scan.history_rows(candidate))
        url = audit.archived_replay_source(rnd) if replay else scan.fwp_round_url(rnd)
        try:
            if url not in cache:
                raw = fetch(url)
                if replay:
                    audit.validate_archived_replay_page(raw, rnd, url)
                else:
                    scan.validate_fwp_round_page(raw, rnd, url)
                cache[url] = raw
            observations = scan.dedupe_observations(
                scan.parse_fwp_observations(cache[url], [fixture], url)
                + scan.parse_fwp_observations(live_html, [fixture], scan.FWP_LIVE_URL))
        except (OSError, ValueError, SystemExit) as exc:
            failures.append({'round': rnd, 'url': url, 'reason': str(exc)})
            continue
        observations = [item for item in observations if item['observation'].get('date') == hold['date']]
        decisions = classify_batch(observations, scan.history_rows(candidate))
        for decision in decisions:
            outcome = decision.get('outcome') or {}
            if outcome.get('kind') == 'result':
                scan.merge_result(candidate, outcome['result'])
                recovered.append(outcome['result'])
        retain_holds(candidate, decisions)
    candidate = resolve_verified_slots(candidate, recovered)
    return candidate, {'changed': candidate != data, 'retried': len(pending),
                       'recovered': len(recovered), 'source_failures': failures}


def scan_unfinished_archived_ties(data, fetch, live_html=''):
    """Check due originals absent from chronology, including ties never held."""
    import auto_round_results as scan
    import auto_draw as draw

    today = datetime.now(timezone.utc).date().isoformat()
    current = base_round(data.get('source_round'))
    history_by_day = defaultdict(list)
    for result in scan.history_rows(data):
        history_by_day[(result.get('round'), result.get('date'))].append(result)
    completed = {(*key, pair_key(row)) for key, rows in history_by_day.items() for row in rows}
    holds_by_day = defaultdict(list)
    for hold in data.get('pending_match_decisions', []):
        fixture = hold['fixture']
        holds_by_day[(fixture.get('round'), hold['date'])].append(fixture)

    candidate = copy.deepcopy(data)
    failures, recovered = [], []
    checked = 0
    current_index = draw.ROUND_ORDER.index(current)
    for rnd in draw.ROUND_ORDER[:current_index]:
        pending = []
        for fixture in draw.fixture_values((data.get('round_fixtures') or {}).get(rnd) or {}):
            day = fixture.get('date')
            if (not day or day > today or fixture.get('round') != rnd
                    or draw.is_conditional_fixture(fixture)):
                continue
            key = (rnd, day)
            if (*key, pair_key(fixture)) in completed or any(
                   scan.match_fixture([fixture], row['home'], row['away'])
                   for row in history_by_day[key] + holds_by_day[key]):
                continue
            pending.append(fixture)
        if not pending:
            continue
        checked += len(pending)
        url = scan.fwp_round_url(rnd)
        try:
            raw = fetch(url)
            scan.validate_fwp_round_page(raw, rnd, url)
            observations = scan.dedupe_observations(
                scan.parse_fwp_observations(raw, pending, url)
                + scan.parse_fwp_observations(live_html, pending, scan.FWP_LIVE_URL))
        except (OSError, ValueError, SystemExit) as exc:
            failures.append({'round': rnd, 'url': url, 'reason': str(exc)})
            continue
        observations = [item for item in observations
                        if item['observation'].get('date') == item['fixture']['date']]
        decisions = classify_batch(observations, scan.history_rows(candidate))
        for decision in decisions:
            outcome = decision.get('outcome') or {}
            if outcome.get('kind') == 'result':
                result = outcome['result']
                if scan.merge_result(candidate, result):
                    recovered.append(result)
            elif outcome.get('kind') == 'event':
                scan.merge_event(candidate, outcome['event'])
        retain_holds(candidate, decisions)

    candidate = resolve_verified_slots(candidate, recovered)
    return candidate, {'changed': candidate != data, 'checked': checked,
                       'recovered': len(recovered), 'source_failures': failures}



def resolve_verified_slots(data, results):
    """Resolve only the immediate next round and a unique two-club slot."""
    import auto_draw as draw
    current = base_round(data.get('source_round'))
    fixtures = draw.fixture_values(data.get('fixtures') or {})
    changed = False
    for result in results:
        rnd = base_round(result['round'])
        if rnd not in draw.ROUND_ORDER or draw.ROUND_ORDER.index(rnd) + 1 >= len(draw.ROUND_ORDER):
            continue
        if draw.ROUND_ORDER[draw.ROUND_ORDER.index(rnd) + 1] != current:
            continue
        matches = []
        for fixture in fixtures:
            for side in ('home', 'away'):
                options = draw.alternatives(fixture.get(side, ''))
                if len(options) != 2:
                    continue
                if ((draw.compatible(options[0], result['home']) and draw.compatible(options[1], result['away']))
                        or (draw.compatible(options[1], result['home']) and draw.compatible(options[0], result['away']))):
                    matches.append((fixture, side, options))
        if len(matches) > 1:
            raise ValueError('recovered winner maps to multiple current draw slots')
        if matches:
            fixture, side, options = matches[0]
            winners = [o for o in options if draw.compatible(o, result['winner'])]
            if len(winners) != 1:
                raise ValueError('recovered winner is ambiguous in current slot')
            fixture[side] = winners[0]
            if not draw.is_conditional_fixture(fixture):
                fixture.pop('conditional', None)
            changed = True
    if changed:
        data = copy.deepcopy(data)
        data['fixtures'] = draw.fixture_map(fixtures)
    return data
