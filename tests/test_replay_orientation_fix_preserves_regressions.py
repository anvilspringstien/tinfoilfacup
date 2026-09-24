"""A replay-orientation repair must not overwrite newer rendered journey tests."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "updater/apply_replay_orientation_fix.py",
    "updater/auto_results.py",
    "updater/patch_clubfinder_competition_logic.py",
    "updater/clubfinder_render_regression.js",
)


class ReplayOrientationRegressionPreservation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative in SOURCES:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        self.render = self.root / "updater/clubfinder_render_regression.js"
        self.repair = self.root / "updater/apply_replay_orientation_fix.py"

    def run_repair(self):
        return subprocess.run(
            [sys.executable, str(self.repair)],
            cwd=self.root, capture_output=True, text=True, check=False,
        )

    def test_two_repairs_preserve_thame_regression_byte_for_byte(self):
        before = self.render.read_bytes()
        self.assertIn(b"exmouthSecondQReplay", before)
        for _ in range(2):
            completed = self.run_repair()
            self.assertEqual(completed.returncode, 0,
                             completed.stdout + completed.stderr)
            self.assertEqual(self.render.read_bytes(), before)
            self.assertIn("regressions preserved", completed.stdout)

    def test_stale_custodian_assertion_fails_closed(self):
        original = self.render.read_text(encoding="utf-8")
        marker = "Thame should become custodian after verified Exmouth 1–3 Thame replay"
        self.assertEqual(original.count(marker), 1)
        stale = original.replace(marker,
            "Exmouth Town should remain custodian after winning replay")
        self.render.write_text(stale, encoding="utf-8")
        completed = self.run_repair()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("coverage is stale or incomplete",
                      completed.stdout + completed.stderr)
        self.assertEqual(self.render.read_text(encoding="utf-8"), stale)


if __name__ == "__main__":
    unittest.main()
