"""Run production/Health and BETA snapshot guards on disposable round states."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from round_transition_fixture import ROOT, STATES, states


def publication_commands():
    """Keep the rehearsal aligned with actual read-only publication guards.

    Source collection, builders, report generation and git writes are excluded.
    Both workflows' standalone Python/Node regression scripts are included.
    """
    commands = []
    for name in ('scan-results.yml', 'competition-health.yml'):
        workflow = (ROOT / '.github/workflows' / name).read_text()
        for runtime, script in re.findall(r'^\s*(?:run: )?(python|node) (updater/[\w]+regression[\w]*\.(?:py|js)|updater/competition_regression_guard.py)\s*$', workflow, re.M):
            command = [sys.executable if runtime == 'python' else 'node', script]
            if command not in commands:
                commands.append(command)
    assert [sys.executable, 'updater/unicorn_replay_regression.py'] in commands
    assert ['node', 'updater/journey_integrity_regression.js'] in commands
    assert ['node', 'updater/historical_venue_regression.js'] in commands
    commands += [
        ['node', 'updater/beta_campaign_identity_regression.js'],
        ['node', 'tests/test_beta_thame_next_fixture.js'],
        ['node', 'tests/test_beta_verified_conditional_replay.js'],
        ['node', 'tests/test_beta_weston_replay_stats.js'],
        ['node', 'tests/test_beta_stats_conditional_next_draw.js'],
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_beta_embedded_snapshot_refresh.py', '-v'],
        [sys.executable, 'updater/refresh_beta_embedded_snapshot.py', '--check'],
    ]
    return commands


def run(command, destination):
    print('+ ' + ' '.join(command), flush=True)
    subprocess.run(command, cwd=destination, check=True, timeout=600)


def write_state(destination, data):
    (destination / 'competition.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    for script in ('refresh_clubfinder_embedded_snapshot.py', 'refresh_beta_embedded_snapshot.py'):
        run([sys.executable, 'updater/' + script], destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', choices=STATES, required=True)
    args = parser.parse_args()
    protected = ('competition.json', 'clubfinder.html', 'beta/clubfinder-beta.html', 'beta/competition-fallback.json')
    checksums = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in protected}
    try:
        data = states(args.state)[args.state]
        with tempfile.TemporaryDirectory(prefix='tffc-round-rehearsal-') as tmp:
            destination = Path(tmp) / 'repo'
            shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns('.git', '__pycache__', 'node_modules', 'assets'))
            write_state(destination, data)
            for command in publication_commands():
                run(command, destination)
    finally:
        for name, digest in checksums.items():
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name + ' changed'
    print('ROUND TRANSITION PUBLICATION REHEARSAL: PASS — ' + args.state, flush=True)


if __name__ == '__main__':
    main()
