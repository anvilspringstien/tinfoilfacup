import datetime as dt
import unittest
from barry_live_watch import verdict, parse_time

NOW = parse_time("2026-10-14T12:00:00Z")

def run(stamp, conclusion="success", status="completed", event="schedule", branch="main"):
    return dict(created_at=stamp, updated_at=stamp, conclusion=conclusion,
                status=status, event=event, head_branch=branch, html_url="https://github.com/example")

class LiveWatchTests(unittest.TestCase):
    def test_recent_success(self):
        self.assertEqual(verdict([run("2026-10-14T11:00:00Z")], NOW)[0], "OK")

    def test_stale(self):
        self.assertEqual(verdict([run("2026-10-14T08:00:00Z")], NOW)[0], "STALE")

    def test_failure(self):
        self.assertEqual(verdict([run("2026-10-14T11:00:00Z", conclusion="failure")], NOW)[0], "FAILED")

    def test_unfinished(self):
        self.assertEqual(verdict([run("2026-10-14T11:00:00Z", status="in_progress")], NOW)[0], "UNFINISHED")

    def test_missing(self):
        self.assertEqual(verdict([], NOW)[0], "NO_SCHEDULED_RUN")

    def test_manual_ignored(self):
        self.assertEqual(verdict([run("2026-10-14T11:00:00Z", event="workflow_dispatch")], NOW)[0], "NO_SCHEDULED_RUN")

    def test_wrong_branch_ignored(self):
        self.assertEqual(verdict([run("2026-10-14T11:00:00Z", branch="beta")], NOW)[0], "NO_SCHEDULED_RUN")

    def test_latest_scheduled_wins(self):
        rows = [run("2026-10-14T10:00:00Z"),
                run("2026-10-14T11:00:00Z", conclusion="failure")]
        self.assertEqual(verdict(rows, NOW)[0], "FAILED")

if __name__ == "__main__":
    unittest.main()
