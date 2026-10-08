"""Protect explicit opt-in publication of archived replay candidates."""
import re
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


if __name__ == "__main__":
    unittest.main()
