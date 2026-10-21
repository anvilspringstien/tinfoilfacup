"""Fixture-local, source-attributed decisions shared by active and archived scans.

A completed level score is never evidence of who won. An explicit, consistent
penalty decision from an accepted publisher is enough; different pages from one
publisher are not independent corroboration of contradictory outcomes.
"""
from collections import defaultdict
from datetime import datetime, timezone
from urllib.parse import urlsplit

from round_state_engine import base_round, classify_observation, norm, pair_key


def publisher(url):
    parsed = urlsplit(str(url or ''))
    if parsed.scheme != 'https' or parsed.username or parsed.password:
        return ''
    host = (parsed.hostname or '').removeprefix('www.')
    if host == 'footballwebpages.co.uk' and (parsed.path == '/fa-cup' or parsed.path.startswith('/fa-cup/')):
        return host
    if host == 'thefa.com' and parsed.path.startswith('/competitions/thefacup/'):
        return host
    return ''


def penalty_observation(row):
    """Validate explicit penalty facts without inferring a match winner."""
    row = dict(row)
    if row.get('decision') != 'penalties' and not any(k in row for k in ('home_pens', 'away_pens')):
        return row
    if not publisher(row.get('source_url')):
        raise ValueError('penalty decision has no accepted source')
    if not str(row.get('status') or '').upper().startswith('FT'):
        raise ValueError('penalty decision is not marked completed')
    if not isinstance(row.get('home_score'), int) or row['home_score'] != row.get('away_score'):
        raise ValueError('penalty decision with non-level source score: corroboration required')
    if any(k in row for k in ('home_pens', 'away_pens')):
        hp, ap = row.get('home_pens'), row.get('away_pens')
        if type(hp) is not int or type(ap) is not int or min(hp, ap) < 0 or hp == ap:
            raise ValueError('incomplete or level shoot-out score')
        winner = row['home'] if hp > ap else row['away']
        if row.get('winner') and norm(row['winner']) != norm(winner):
            raise ValueError('penalty winner contradicts shoot-out score')
        row['winner'] = winner
    if not row.get('winner'):
        raise ValueError('completed level fixture awaiting penalty decision')
    if norm(row.get('winner')) not in pair_key(row):
        raise ValueError('penalty decision requires an explicit participating winner')
    row['decision'] = 'penalties'
    return row


def signature(row):
    return (row.get('round'), row.get('date'), norm(row.get('home')), norm(row.get('away')),
            row.get('home_score'), row.get('away_score'), norm(row.get('winner')),
            None if str(row.get('status') or '').startswith('FT') else row.get('status'))


def classify_batch(items, history):
    """Account for each dated fixture once; never merge a partially held tie.

    Ambiguous mappings are rejected by the parser before entry. Conflicts in one
    mapped tie remain local. Canonical chronology is still enforced by the shared
    state engine and every published candidate passes the global guards.
    """
    groups = defaultdict(list)
    for item in items:
        fixture, row = item['fixture'], item['observation']
        if len(pair_key(fixture)) != 2 or not row.get('date'):
            raise ValueError('incomplete canonical observation identity')
        groups[(base_round(fixture.get('round')), pair_key(fixture), row['date'])].append(item)
    decisions = []
    local_history = list(history)
    for (_, pair, _), group in sorted(groups.items(), key=lambda item: item[0][2]):
        fixture = group[0]['fixture']
        rows = [item['observation'] for item in group]
        sources = sorted({row['source_url'] for row in rows if row.get('source_url')})
        valid, incomplete, errors = [], [], []
        for row in rows:
            try:
                normalized = penalty_observation(row)
                relevant = [r for r in local_history if pair_key(r) == pair
                            and base_round(r.get('round')) == base_round(fixture.get('round'))]
                # A source dropping its winner note is an omission, not a
                # correction of an already verified, identical level result.
                if (str(normalized.get('status') or '').startswith('FT')
                        and normalized.get('home_score') == normalized.get('away_score')
                        and not normalized.get('winner')):
                    recorded = [r for r in relevant if r.get('date') == normalized.get('date')
                                and norm(r.get('home')) == norm(normalized.get('home'))
                                and norm(r.get('away')) == norm(normalized.get('away'))
                                and r.get('home_score') == normalized.get('home_score')
                                and r.get('away_score') == normalized.get('away_score') and r.get('winner')]
                    if len({signature(r) for r in recorded}) == 1:
                        valid.append(({'kind': 'duplicate', 'result': recorded[0]}, row))
                        continue
                outcome = classify_observation(fixture, normalized, relevant)
                if outcome['kind'] == 'duplicate':
                    recorded = outcome['result']
                    if ('home_pens' in normalized and 'home_pens' in recorded
                            and (normalized['home_pens'], normalized['away_pens']) != (recorded['home_pens'], recorded['away_pens'])):
                        raise ValueError('shoot-out scores conflict with the verified historical result')
                # The classifier can recognise a level explicit winner as penalties.
                if outcome['kind'] == 'result' and outcome['result'].get('decision') == 'penalties':
                    penalty_observation(outcome['result'])
                valid.append((outcome, row))
            except ValueError as exc:
                if ((str(exc).startswith('level ') and 'requires explicit' in str(exc))
                        or str(exc) == 'completed level fixture awaiting penalty decision'):
                    incomplete.append(row)
                else:
                    errors.append(str(exc))
        # Missing winner text is a refinement only if all match facts agree.
        for row in incomplete:
            matching = [outcome for outcome, observed in valid
                        if outcome['kind'] in ('result', 'duplicate')
                        and observed.get('date') == row.get('date')
                        and norm(observed.get('home')) == norm(row.get('home'))
                        and norm(observed.get('away')) == norm(row.get('away'))
                        and observed.get('home_score') == row.get('home_score')
                        and observed.get('away_score') == row.get('away_score')
                        and outcome['result'].get('winner')]
            if not matching:
                errors.append('completed level fixture awaiting penalty decision')
        variants = defaultdict(list)
        for outcome, row in valid:
            result = outcome.get('result') or outcome.get('event')
            variants[signature(result)].append((outcome, row))
        if len(variants) > 1 and not errors:
            # An explicit FA decision can settle a conflicting secondary feed.
            official = [entries for entries in variants.values()
                        if any(publisher(row.get('source_url')) == 'thefa.com' for _, row in entries)]
            corroborated = [entries for entries in variants.values()
                            if len({publisher(row.get('source_url')) for _, row in entries} - {''}) >= 2]
            choices = official if len(official) == 1 else corroborated
            if len(choices) == 1:
                variants = {signature(choices[0][0][0].get('result') or choices[0][0][0].get('event')): choices[0]}
            else:
                errors.append('conflicting source outcomes require corroboration')
        if len(variants) == 1 and not errors:
            entries = next(iter(variants.values()))
            shootouts = {(row['home_pens'], row['away_pens']) for _, row in entries
                         if 'home_pens' in row and 'away_pens' in row}
            if len(shootouts) > 1:
                official = [entry for entry in entries if publisher(entry[1].get('source_url')) == 'thefa.com']
                if len(official) == 1:
                    variants = {next(iter(variants)): official}
                else:
                    errors.append('conflicting shoot-out scores require corroboration')
        if errors or not variants:
            reason = '; '.join(sorted(set(errors))) or 'completed fixture awaiting penalty decision'
            decisions.append({'fixture': fixture, 'observation': rows[0], 'sources': sources,
                              'held': reason, 'state': 'awaiting-decision' if 'awaiting' in reason else 'conflicting-evidence'})
            continue
        entries = next(iter(variants.values()))
        preferred = next((o for o, r in entries if 'home_pens' in r), entries[0][0])
        outcome = next((o for o, _ in entries if o['kind'] == 'duplicate'), preferred)
        if outcome['kind'] == 'result' and outcome['result'].get('decision') == 'penalties':
            outcome = dict(outcome, result=dict(outcome['result'], decision_sources=sources))
        decisions.append({'fixture': fixture, 'outcome': outcome, 'sources': sources,
                          'refined_observations': len(incomplete)})
        if outcome['kind'] == 'result':
            local_history.append(outcome['result'])
    # A later conflict for the same canonical tie cannot leave an earlier new
    # result from this scan eligible for publication.
    held_pairs = {pair_key(d['fixture']) for d in decisions if d.get('held')}
    return [d if d.get('held') or pair_key(d['fixture']) not in held_pairs
            else dict(fixture=d['fixture'], observation=(d['outcome'].get('result') or d['outcome'].get('event')),
                      sources=d['sources'], held='another observation for this tie is quarantined', state='conflicting-evidence')
            for d in decisions]


def hold_key(hold):
    return (base_round(hold['fixture'].get('round')), pair_key(hold['fixture']), hold['date'])


def retain_holds(data, decisions):
    """Keep unresolved fixture identities across draws without storing guesses."""
    old = {hold_key(h): h for h in data.get('pending_match_decisions', [])}
    pending = dict(old)
    for decision in decisions:
        row = decision.get('observation') or decision.get('outcome', {}).get('result') or decision.get('outcome', {}).get('event')
        if not row:
            continue
        key = (base_round(decision['fixture'].get('round')), pair_key(decision['fixture']), row['date'])
        if decision.get('held'):
            pending[key] = {'fixture': decision['fixture'], 'date': row['date'],
                            'reason': decision['held'], 'state': decision['state'], 'sources': decision['sources'],
                            'first_seen_at': old.get(key, {}).get('first_seen_at') or datetime.now(timezone.utc).isoformat()}
        elif decision.get('outcome', {}).get('kind') in ('result', 'duplicate'):
            pending.pop(key, None)
    values = sorted(pending.values(), key=lambda h: (h['date'], h['fixture']['home'], h['fixture']['away']))
    changed = values != data.get('pending_match_decisions', [])
    if values or 'pending_match_decisions' in data:
        data['pending_match_decisions'] = values
    return changed
