#!/usr/bin/env python3
"""Refresh BETA's separate fallback from canonical competition.json."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BETA = ROOT / 'beta/clubfinder-beta.html'
DATA = ROOT / 'competition.json'
FALLBACK = ROOT / 'beta/competition-fallback.json'


def refresh(html, data):
    if data.get('schema_version') != 1 or not data.get('updated_at'):
        raise ValueError('Canonical competition schema/timestamp missing')
    if not data.get('result_history') or not data.get('fixtures'):
        raise ValueError('Canonical result history/fixtures missing')
    required = (
        "const BETA_COMPETITION_DATA_URL='./competition-fallback.json';",
        "const PRODUCTION_COMPETITION_DATA_URL='../competition.json';",
        "let LIVE_COMPETITION_DATA=null;",
        "const d=await loadSource(PRODUCTION_COMPETITION_DATA_URL,'canonical');",
        "const d=await loadSource(BETA_COMPETITION_DATA_URL,'BETA fallback');",
        "LIVE_DATA_STATUS={state:'live'",
        "LIVE_DATA_STATUS={state:'fallback'",
        "LIVE_DATA_STATUS={state:'unavailable'",
        "if(!d||Number(d.schema_version)!==1||!d.updated_at||!d.results||!d.fixtures)",
    )
    if any(html.count(x) != 1 for x in required):
        raise ValueError('BETA canonical-first/fallback loader boundary changed')
    loader = html.split('async function refreshCompetitionData(force=false){', 1)
    if len(loader) != 2:
        raise ValueError('BETA refresh function missing')
    loader = loader[1].split('function updateLiveDataBadge(){', 1)[0]
    if (loader.index('loadSource(PRODUCTION_COMPETITION_DATA_URL') >=
            loader.index('loadSource(BETA_COMPETITION_DATA_URL')):
        raise ValueError('BETA canonical source must precede fallback')
    if 'EMBEDDED_COMPETITION_DATA' in html:
        raise ValueError('BETA still contains an embedded snapshot')
    return json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    live = json.loads(DATA.read_text(encoding='utf-8'))
    expected = refresh(BETA.read_text(encoding='utf-8'), live)
    current = FALLBACK.read_text(encoding='utf-8') if FALLBACK.exists() else None
    if args.check and current != expected:
        raise SystemExit('BETA FALLBACK GUARD: FAIL — fallback asset is stale')
    if not args.check and current != expected:
        FALLBACK.write_text(expected, encoding='utf-8')
    print('BETA FALLBACK GUARD: PASS')
    print('Canonical competition updated_at:', live['updated_at'])
    print('Mode:', 'check-only' if args.check else 'refresh')
    print('Production files: untouched')


if __name__ == '__main__':
    main()
