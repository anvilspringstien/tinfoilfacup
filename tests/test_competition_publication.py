"""Exercise publication races with local git remotes, plus workflow contracts."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'updater'))
from guard_publication_base import changed_inputs


def git(cwd, *args):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def configure(path):
    git(path, 'config', 'user.name', 'Publication Test')
    git(path, 'config', 'user.email', 'publication@example.test')


class PublicationTests(unittest.TestCase):
    def make_repositories(self, tmp):
        root = Path(tmp)
        remote = root/'remote.git'
        git(root, 'init', '--bare', '--initial-branch=main', str(remote))
        first = root/'first'
        git(root, 'clone', str(remote), str(first))
        configure(first)
        (first/'competition.json').write_text(json.dumps({'draw': 'old', 'preserved_history': {'original': 'drawn', 'round': 'qualifying', 'date': 'Saturday', 'venue': 'original ground', 'kickoff': '15:00', 'miles': 24}, 'result': 'old'}, indent=2)+'\n')
        (first/'beta').mkdir()
        (first/'beta/competition-check-status.json').write_text('{}\n')
        git(first, 'add', '.')
        git(first, 'commit', '-m', 'Initial state')
        git(first, 'push', 'origin', 'main')
        second = root/'second'
        git(root, 'clone', str(remote), str(second))
        configure(second)
        return root, remote, first, second

    def test_simultaneous_draw_result_candidates_never_overwrite_newer_inputs(self):
        for first_field, second_field in [('draw', 'result'), ('result', 'draw')]:
            with self.subTest(first=first_field), tempfile.TemporaryDirectory() as tmp:
                _, remote, first, second = self.make_repositories(tmp)
                base = git(second, 'rev-parse', 'HEAD')
                for repo, field in [(first, first_field), (second, second_field)]:
                    data = json.loads((repo/'competition.json').read_text())
                    data[field] = 'new'
                    (repo/'competition.json').write_text(json.dumps(data, indent=2)+'\n')
                    git(repo, 'add', '.')
                    git(repo, 'commit', '-m', 'Candidate '+field)
                git(first, 'push', 'origin', 'main')
                # Even a clean textual rebase is not evidence the stale candidate
                # was validated against the newer canonical inputs.
                git(second, 'pull', '--rebase', 'origin', 'main')
                self.assertEqual(changed_inputs(base, 'origin/main', second), ['competition.json'])
                result = subprocess.run([sys.executable, str(ROOT/'updater/guard_publication_base.py'),
                                         '--base', base, '--upstream', 'origin/main'], cwd=second, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('STALE COMPETITION CANDIDATE', result.stderr)
                published = json.loads(git(remote, 'show', 'main:competition.json'))
                self.assertEqual(published[first_field], 'new')
                self.assertEqual(published[second_field], 'old')

    def test_independent_status_rebase_keeps_both_updates_and_revalidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, remote, first, second = self.make_repositories(tmp)
            base = git(second, 'rev-parse', 'HEAD')
            (first/'beta/competition-check-status.json').write_text('{"state":"checked"}\n')
            git(first, 'add', '.')
            git(first, 'commit', '-m', 'New status')
            git(first, 'push', 'origin', 'main')
            data = json.loads((second/'competition.json').read_text())
            data['result'] = 'new'
            (second/'competition.json').write_text(json.dumps(data, indent=2)+'\n')
            git(second, 'add', '.')
            git(second, 'commit', '-m', 'Results candidate')
            git(second, 'pull', '--rebase', 'origin', 'main')
            self.assertEqual(changed_inputs(base, 'origin/main', second), [])
            # Validate the actual rebased candidate, then push without force.
            self.assertEqual(json.loads((second/'competition.json').read_text())['result'], 'new')
            self.assertEqual(json.loads((second/'beta/competition-check-status.json').read_text())['state'], 'checked')
            git(second, 'push', 'origin', 'HEAD:main')
            self.assertEqual(json.loads(git(remote, 'show', 'main:competition.json'))['result'], 'new')

    def test_queued_checkout_reresolves_head_instead_of_using_event_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _, first, second = self.make_repositories(tmp)
            event_sha = git(second, 'rev-parse', 'HEAD')
            (first/'new-input.txt').write_text('new upstream input')
            git(first, 'add', '.')
            git(first, 'commit', '-m', 'Advance while queued')
            git(first, 'push', 'origin', 'main')
            git(second, 'fetch', 'origin', 'main')
            git(second, 'checkout', '-B', 'main', 'origin/main')
            self.assertNotEqual(git(second, 'rev-parse', 'HEAD'), event_sha)
            self.assertTrue((second/'new-input.txt').exists())
            self.assertEqual(changed_inputs(event_sha, 'origin/main', second), ['new-input.txt'])

    def test_invalid_rebased_candidate_is_never_pushed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, remote, first, second = self.make_repositories(tmp)
            original = git(remote, 'rev-parse', 'main')
            base = git(second, 'rev-parse', 'HEAD')
            (second/'competition.json').write_text('invalid json')
            git(second, 'add', '.')
            git(second, 'commit', '-m', 'Invalid candidate')
            git(second, 'pull', '--rebase', 'origin', 'main')
            self.assertEqual(changed_inputs(base, 'origin/main', second), [])
            validation = subprocess.run([sys.executable, '-m', 'json.tool', 'competition.json'], cwd=second, capture_output=True)
            self.assertNotEqual(validation.returncode, 0)
            self.assertEqual(git(remote, 'rev-parse', 'main'), original)

    def test_every_competition_lock_participant_retains_waiting_runs(self):
        participants=[]
        for path in (ROOT/'.github/workflows').glob('*.yml'):
            workflow=path.read_text()
            if 'competition-state-' not in workflow:
                continue
            participants.append(path.name)
            block=workflow.split('\nconcurrency:\n',1)[1].split('\njobs:',1)[0]
            self.assertIn('queue: max',block,path.name)
            self.assertIn('cancel-in-progress: false',block,path.name)
            checkout=workflow.split('uses: actions/checkout@',1)[1].split('      - ',1)[0]
            self.assertIn('ref:',checkout,path.name)
        self.assertEqual(len(participants),7)
        status=(ROOT/'.github/workflows/publish-competition-check-status.yml').read_text()
        self.assertIn('queue: max',status.split('\nconcurrency:\n',1)[1].split('\njobs:',1)[0])

    def test_all_writers_share_lock_and_revalidate_after_rebase(self):
        for name in ['scan-draw.yml', 'scan-results.yml', 'competition-health.yml']:
            with self.subTest(workflow=name):
                workflow = (ROOT/'.github/workflows'/name).read_text()
                self.assertIn('group: competition-state-${{ github.ref_name }}', workflow)
                self.assertIn('cancel-in-progress: false', workflow)
                checkout = workflow.split('uses: actions/checkout@v5',1)[1].split('      - ',1)[0]
                self.assertIn('ref: ${{ github.ref_name }}', checkout)
                self.assertIn('git rev-parse HEAD > "$RUNNER_TEMP/competition-build-base"', workflow)
                after = workflow.split('git pull --rebase',1)[1]
                self.assertLess(after.index('guard_publication_base.py'), after.index('competition_regression_guard.py'))
                self.assertLess(after.index('competition_regression_guard.py'), after.index('git push origin'))
                self.assertNotIn('--force', after)


if __name__ == '__main__':
    unittest.main()
