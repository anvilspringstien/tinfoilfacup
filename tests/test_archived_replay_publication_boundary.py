"""Protect explicit opt-in publication of archived replay candidates."""
import re
import copy
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/publish-preceding-replays.yml"


class PublicationBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_dispatch_requires_default_off_boolean(self):
        self.assertIn("  workflow_dispatch:\n    inputs:\n      publish:", self.workflow)
        dispatch = self.workflow.split("  workflow_dispatch:", 1)[1].split("\npermissions:", 1)[0]
        publish = dispatch.split("      publish:", 1)[1]
        self.assertIn("        type: boolean", publish)
        self.assertIn("        required: true", publish)
        self.assertIn("        default: false", publish)

    def test_publication_requires_main_manual_opt_in_and_staged_changes(self):
        block = self.workflow.split("      - name: Publish guarded candidate only after all isolated guards pass", 1)[1]
        condition = block.split("\n", 2)[1].strip()
        for required in ("github.ref_name == 'main'", "github.event_name == 'workflow_dispatch'",
                         "inputs.publish == true", "steps.stage.outputs.has_changes == 'true'"):
            self.assertIn(required, condition)
        self.assertNotIn("github.event_name != 'pull_request'", condition)

    def test_staging_and_simulation_precede_publication(self):
        positions = [self.workflow.index(name) for name in (
            "- name: Produce read-only source-backed promotion readiness report",
            "- name: Stage real preceding-round replay candidates in memory",
            "- name: Simulate full candidate state in isolated workspace",
            "- name: Guard complete accounting and conditional independent promotion",
            "- name: Publish guarded candidate only after all isolated guards pass")]
        self.assertEqual(positions, sorted(positions))

    def run_accounting_gate(self, tamper=False):
        sys.path.insert(0, str(WORKFLOW.parents[2] / 'updater'))
        from guard_archived_replay_promotion import readiness
        rows = [dict(home='Anstey Nomads', away='Macclesfield', date='2026-10-20',
                     round='Fourth Round Qualifying Replay', home_score=0, away_score=3,
                     winner='Macclesfield', decision=''),
                dict(home='Cray Wanderers', away='Bedford Town', date='2026-10-20',
                     round='Fourth Round Qualifying Replay', home_score=2, away_score=2,
                     winner='Cray Wanderers', decision='penalties')]
        audit = dict(production_mutation=False, archived_round='Fourth Round Qualifying',
                     replay_candidates=rows, blocked=[], events=[], observations=2, already_recorded=0,
                     scheduled_replay_gaps=[dict(home=r['home'], away=r['away'], date=r['date'],
                                                 source_observed=True) for r in rows])
        report = readiness(audit)
        if tamper:
            report['approved'].append(copy.deepcopy(rows[1]))
            report.update(approved_count=2, held_count=0, held=[])
        block = self.workflow.split('      - name: Guard complete accounting and conditional independent promotion', 1)[1]
        script = textwrap.dedent(block.split("          python - <<'PY'\n", 1)[1].split('\n          PY', 1)[0])
        with tempfile.TemporaryDirectory() as tmp:
            for filename, value in [('replay-promotion-readiness.json', report),
                                    ('archived-replay-audit.json', audit),
                                    ('replay-independent-evidence.json', {})]:
                (Path(tmp) / filename).write_text(json.dumps(value))
            return subprocess.run([sys.executable, '-c', script.replace('/tmp/', tmp + '/')],
                                  cwd=WORKFLOW.parents[2], capture_output=True, text=True)

    def test_accounting_allows_generic_held_penalty_and_unrelated_clear_result(self):
        result = self.run_accounting_gate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('1 new cleared, 1 held', result.stdout)

    def test_accounting_rejects_forged_approval_of_held_penalty(self):
        result = self.run_accounting_gate(tamper=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('readiness report differs', result.stderr)


if __name__ == "__main__":
    unittest.main()
