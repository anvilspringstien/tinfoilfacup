"""Retry durable fixture holds after the active draw has advanced."""
import copy

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
                raise ValueError('recovered penalty winner is ambiguous in current slot')
            fixture[side] = winners[0]
            if not draw.is_conditional_fixture(fixture):
                fixture.pop('conditional', None)
            changed = True
    if changed:
        data = copy.deepcopy(data)
        data['fixtures'] = draw.fixture_map(fixtures)
    return data
