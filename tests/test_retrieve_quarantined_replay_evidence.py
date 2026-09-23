import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "updater"))
from retrieve_quarantined_replay_evidence import extract, retrieve, SOURCES, WIMBORNE
from reconcile_quarantined_replay_evidence import reconcile

CLUB = """<html>First Team Latest Result FA Cup Second Round Qualifying Replay Tue 22 September Wyatt Homes Stadium Wimborne Town 1 (4) Weston-super-Mare 1 (3) 1-1 (4-3 pens)</html>"""
NEWS = """<html>TUESDAY SEPTEMBER 22, 2026 Wimborne Town 1-1 Weston-super-Mare AFC AET 0-0 @ FT Wimborne win 4-3 on pens</html>"""

class LiveRecoveryTests(unittest.TestCase):
    def test_both_independent_publishers_resolve_quarantine(self):
        pages = {SOURCES[0][1]: CLUB, SOURCES[1][1]: NEWS}
        evidence, failures = retrieve(lambda url: pages[url])
        self.assertEqual(failures, [])
        self.assertEqual(reconcile(WIMBORNE, evidence)["status"], "independently_verified")
    def test_saturday_original_draw_cannot_resolve_replay(self):
        self.assertIsNone(extract(SOURCES[0][0], SOURCES[0][1], CLUB.replace("Tue 22", "Sat 19")))
    def test_conflicting_regional_report_fails_closed(self):
        pages = {SOURCES[0][1]: CLUB, SOURCES[1][1]: NEWS.replace("4-3", "5-4")}
        evidence, failures = retrieve(lambda url: pages[url])
        self.assertEqual(len(evidence), 1)
        self.assertEqual(reconcile(WIMBORNE, evidence)["status"], "quarantined")
    def test_unavailable_source_fails_closed(self):
        evidence, failures = retrieve(lambda url: CLUB if url == SOURCES[0][1] else (_ for _ in ()).throw(TimeoutError()))
        self.assertEqual(len(failures), 1)
        self.assertEqual(reconcile(WIMBORNE, evidence)["status"], "quarantined")

if __name__ == "__main__":
    unittest.main()
