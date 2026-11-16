"""Rebuild a Results candidate from captured public source HTML in a temp checkout.

No production input is changed. The 17 October failed candidate wasn't retained;
this is an explicit reconstruction from the 18 October source capture.
"""
from pathlib import Path
import argparse
import gzip
import json
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'updater'))
sys.path.insert(0, str(ROOT / 'tests'))
import auto_round_results as scan
import enrich_replay_kickoffs_and_active_venues as enrich
from result_metadata import preserve_result_metadata
from test_results_repair import FIXTURES, source_fetch, replay_result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', help='Rerun one named rendered check after fixing a test; default runs all')
    args = parser.parse_args()
    original = json.loads((ROOT / 'competition.json').read_text())
    data = json.loads(gzip.decompress((FIXTURES / 'competition-input.json.gz').read_bytes()))
    rnd, known = scan.active_fixtures(data)
    source = scan.fwp_round_url(rnd)
    raw = (FIXTURES / 'fourth-qualifying-round.html').read_text()
    scan.validate_fwp_round_page(raw, rnd, source)
    observations = scan.dedupe_observations(scan.parse_fwp_observations(raw, known, source))
    history = scan.history_rows(data)
    for item in observations:
        relevant = [r for r in history if scan.pair_key(r) == scan.pair_key(item['fixture'])]
        outcome = scan.classify_observation(item['fixture'], item['observation'], relevant)
        if outcome['kind'] == 'result':
            scan.merge_result(data, outcome['result'])
            history.append(outcome['result'])
    preserve_result_metadata(data)
    with patch.object(enrich, 'fetch', side_effect=source_fetch):
        details, _ = enrich.replay_source_details([replay_result()])
    enrich.apply_replay_kickoffs(data, details)
    replay = next(r for r in scan.history_rows(data) if r.get('round') == 'Third Round Qualifying Replay' and r['home'] == 'Atherton Collieries')
    assert replay['kickoff'] == '19:45'
    assert len(observations) == 32
    print('Reconstructed 32 source observations; recovered replay kick-off from exact match page.', flush=True)
    with tempfile.TemporaryDirectory(prefix='tinfoil-results-candidate-') as tmp:
        destination = Path(tmp) / 'repo'
        shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns('.git', '__pycache__', 'node_modules', 'assets'))
        (destination / 'competition.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
        commands = [
            [sys.executable, 'updater/refresh_clubfinder_embedded_snapshot.py'],
            [sys.executable, 'updater/competition_regression_guard.py'],
            [sys.executable, 'updater/reconcile_result_history_aliases.py', '--check'],
            [sys.executable, 'updater/kickoff_venue_regression.py'],
            [sys.executable, 'updater/competition_health.py'],
        ]
        for name in ('clubfinder_render', 'clubfinder_stats', 'historical_journey', 'historical_venue',
                     'replay_progression', 'journey_integrity', 'amersham_card_render', 'amersham_stats',
                     'ex8_venue_render', 'kt21_venue_render', 'law2_origin', 'production_ui'):
            if not args.check or args.check == name:
                commands.append(['node', f'updater/{name}_regression.js'])
        if args.check and not any(c[0] == 'node' for c in commands):
            raise ValueError('Unknown rendered check: ' + args.check)
        for command in commands:
            print('+ ' + ' '.join(command), flush=True)
            subprocess.run(command, cwd=destination, check=True)
    assert json.loads((ROOT / 'competition.json').read_text()) == original
    print('RESULTS REPAIR RECONSTRUCTED CANDIDATE: PASS; checks=' + (args.check or 'all') + '; production inputs unchanged.', flush=True)


if __name__ == '__main__':
    main()
