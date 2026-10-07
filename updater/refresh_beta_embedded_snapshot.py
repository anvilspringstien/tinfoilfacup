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
        'fetch(u,{cache:\'no-store\'})',
        "message:'BETA validated competition data loaded'",
        "message:'Production fallback — BETA data unavailable'",
        "LIVE_DATA_STATUS={state:'unavailable'",
    )
    if any(html.count(x) < 1 for x in required):
        raise ValueError('BETA data-source loader boundary changed')
    beta_first = html.find('const u=BETA_COMPETITION_DATA_URL')
    production_fallback = html.find('const u=PRODUCTION_COMPETITION_DATA_URL')
    if beta_first < 0 or production_fallback < 0 or beta_first >= production_fallback:
        raise ValueError('BETA must prefer validated BETA data before production fallback')
    if 'EMBEDDED_COMPETITION_DATA' in html:
        raise ValueError('BETA still contains an embedded snapshot')
    return json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--source', default=str(DATA), help='Competition snapshot that the BETA fallback must match')
    args = parser.parse_args()
    source = Path(args.source)
    if not source.is_absolute():
        source = ROOT / source
    live = json.loads(source.read_text(encoding='utf-8'))
    expected = refresh(BETA.read_text(encoding='utf-8'), live)
    current = FALLBACK.read_text(encoding='utf-8') if FALLBACK.exists() else None
    if args.check and current != expected:
        raise SystemExit('BETA FALLBACK GUARD: FAIL — fallback asset is stale')
    if not args.check and current != expected:
        FALLBACK.write_text(expected, encoding='utf-8')
    print('BETA FALLBACK GUARD: PASS')
    print('Validated BETA source:', source.relative_to(ROOT) if source.is_relative_to(ROOT) else source)
    print('Competition updated_at:', live['updated_at'])
    print('Mode:', 'check-only' if args.check else 'refresh')
    print('Production files: untouched')


if __name__ == '__main__':
    main()
