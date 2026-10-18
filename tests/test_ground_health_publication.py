"""Exercise the actual report publisher with disposable local Git remotes."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

PUBLISHER = Path(__file__).resolve().parents[1] / 'updater/commit_ground_health_reports.sh'
REPORTS = ('ground-health.md', 'updater/ground-health.json',
           'law2-location-verification-audit.md', 'updater/law2-location-verification-audit.json',
           'tester-club-postcodes.csv')


class GroundHealthPublication(unittest.TestCase):
    def git(self, *args, cwd=None):
        return subprocess.check_output(['git', *args], cwd=cwd or self.repo,
                                       stderr=subprocess.STDOUT, text=True).strip()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.remote, self.repo = root / 'origin.git', root / 'monitor'
        self.repo.mkdir()
        self.git('init', '--bare', '--initial-branch=main', str(self.remote))
        self.git('init', '--initial-branch=main')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.test')
        for name in (*REPORTS, 'clubfinder.html', 'competition.json'):
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('baseline\n')
        self.git('add', '.')
        self.git('commit', '-m', 'baseline')
        self.git('remote', 'add', 'origin', str(self.remote))
        self.git('push', '-u', 'origin', 'main')
        self.baseline = self.git('rev-parse', 'HEAD')

    def publish(self):
        return subprocess.run(['bash', str(PUBLISHER)], cwd=self.repo,
                              env={**os.environ, 'GITHUB_REF_NAME': 'main'},
                              text=True, capture_output=True)

    def dirty_audit(self):
        (self.repo / 'clubfinder.html').write_text('temporary audit origin view\n')
        (self.repo / REPORTS[0]).write_text('new health report\n')

    def test_report_publishes_after_dirty_html_and_upstream_advance(self):
        other = Path(self.tmp.name) / 'upstream'
        self.git('clone', str(self.remote), str(other))
        self.git('config', 'user.name', 'Other', cwd=other)
        self.git('config', 'user.email', 'other@example.test', cwd=other)
        (other / 'clubfinder.html').write_text('newer protected presentation\n')
        self.git('add', 'clubfinder.html', cwd=other)
        self.git('commit', '-m', 'upstream presentation', cwd=other)
        self.git('push', cwd=other)
        self.dirty_audit()
        result = self.publish()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git('show', '--format=', '--name-only', 'HEAD'), REPORTS[0])
        self.assertEqual((self.repo / 'clubfinder.html').read_text(), 'newer protected presentation\n')
        self.assertEqual((self.repo / 'competition.json').read_text(), 'baseline\n')
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.git('rev-parse', 'origin/main'))

    def test_unexpected_competition_edit_blocks_publication(self):
        self.dirty_audit()
        (self.repo / 'competition.json').write_text('unexpected result edit\n')
        result = self.publish()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.baseline)
        self.assertEqual(self.git('ls-remote', 'origin', 'refs/heads/main').split()[0], self.baseline)
        self.assertEqual((self.repo / 'competition.json').read_text(), 'unexpected result edit\n')

    def test_unchanged_reports_do_not_create_commit(self):
        (self.repo / 'clubfinder.html').write_text('temporary audit origin view\n')
        result = self.publish()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.baseline)
        self.assertEqual(self.git('status', '--porcelain'), '')


if __name__ == '__main__':
    unittest.main()
