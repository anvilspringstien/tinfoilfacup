"""Keep actual scan recovery, scheduled freshness, and untrusted runs distinct."""
import copy
import datetime as dt
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'updater'))
import publish_competition_check_status as status
NOW = dt.datetime(2026,10,19,11,tzinfo=dt.timezone.utc)


def run(event='push', age=1, **overrides):
    result = dict(id=123, event=event, head_branch='main', head_repository={'full_name': status.REPOSITORY},
                  status='completed', conclusion='success', html_url='https://example.test/run',
                  updated_at=(NOW-dt.timedelta(hours=age)).isoformat().replace('+00:00','Z'))
    result.update(overrides)
    return result


class CheckStatusTests(unittest.TestCase):
    def test_repaired_push_scans_do_not_hide_stale_schedules(self):
        payload = status.build_payload({'results':run(), 'draw':run()},
                                       {'results':run('schedule',age=5), 'draw':run('schedule',conclusion='failure')}, NOW)
        self.assertEqual(payload['state'], 'checked')
        self.assertEqual(payload['scheduled']['state'], 'unverified')
        self.assertEqual(payload['scheduled']['diagnostics']['results']['reason'], 'stale')
        self.assertEqual(payload['scheduled']['diagnostics']['draw']['reason'], 'not_successful')
        self.assertEqual(payload['diagnostics']['draw']['event'], 'push')

    def test_successful_newer_run_never_conceals_failure_or_queue(self):
        for changes, reason in [({'conclusion':'failure'}, 'not_successful'),
                                ({'status':'queued','conclusion':None}, 'not_completed'),
                                ({'age':4}, 'stale'), ({'age':-1}, 'future_timestamp')]:
            with self.subTest(changes=changes):
                payload=status.build_payload({'results':run(), 'draw':run(**changes)}, {'results':run(), 'draw':run()}, NOW)
                self.assertEqual(payload['state'],'unverified')
                self.assertIsNone(payload['last_checked_at'])
                self.assertEqual(payload['diagnostics']['draw']['reason'],reason)

    def test_only_main_repository_pushes_and_schedules_are_trusted(self):
        self.assertTrue(status.eligible(run()))
        self.assertTrue(status.eligible(run('schedule')))
        for row in [run('workflow_dispatch'), run('pull_request'), run(head_branch='feature'),
                    run(head_repository={'full_name':'someone/fork'}), run(head_repository=None)]:
            self.assertFalse(status.eligible(row))
        self.assertFalse(status.eligible(run(), scheduled=True))

    def test_latest_eligible_failure_is_selected_before_older_success(self):
        import io
        rows=[run('pull_request'), run(conclusion='failure',id=2), run(id=1)]
        with patch.dict('os.environ', {'GH_TOKEN':'test'}), patch.object(status.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps({'workflow_runs':rows}).encode())):
            self.assertEqual(status.latest('scan-draw.yml')['id'],2)

    def test_both_fresh_schedules_and_pushes_report_checked(self):
        payload=status.build_payload({'results':run(age=1), 'draw':run(age=2)},
                                     {'results':run('schedule'), 'draw':run('schedule')}, NOW)
        self.assertEqual(payload['state'],'checked')
        self.assertEqual(payload['scheduled']['state'],'checked')
        self.assertEqual(payload['last_checked_at'],run(age=2)['updated_at'])

    def test_callback_trust_boundary_and_recompute_after_rebase(self):
        workflow=(ROOT/'.github/workflows/publish-competition-check-status.yml').read_text()
        self.assertIn("github.event.workflow_run.event == 'push'",workflow)
        self.assertIn('github.event.workflow_run.head_repository.full_name == github.repository',workflow)
        self.assertIn('GH_TOKEN: ${{ github.token }}', workflow.split('- name: Publish only if check status changed',1)[1])
        after=workflow.split('git pull --rebase',1)[1]
        self.assertLess(after.index('python updater/publish_competition_check_status.py'),after.index('git push origin'))


if __name__=='__main__':
    unittest.main()
