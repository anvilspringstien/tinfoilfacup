import datetime as dt
import tempfile
import unittest
from pathlib import Path
from barry_schedule_watchdog import SCANS, inspect, parse_time, read_csv

DATE = dt.date(2026, 10, 13)

def run(name, created, *, event='schedule', conclusion='success', status='completed', ident='1'):
    stamp = parse_time(created)
    return dict(id=ident, name=name, event=event, created=stamp, started=stamp,
                updated=stamp, status=status, conclusion=conclusion, url='https://github.com/example')

class WatchdogTests(unittest.TestCase):
    def test_missing_and_delayed(self):
        rows = [run(SCANS['results'][0], '2026-10-13T03:34:15Z')]
        result = inspect(rows, DATE, parse_time('2026-10-13T05:00:00Z'))['workflows']['results']
        self.assertEqual(result['scheduled_runs'], 1)
        self.assertEqual(result['successes'], 1)
        self.assertEqual(len(result['missing_or_delayed_slots_local']), 3)
        self.assertEqual(result['unmatched_runs'], [])

    def test_failure_is_not_missing(self):
        rows = [run(SCANS['results'][0], '2026-10-13T03:17:00Z', conclusion='failure')]
        result = inspect(rows, DATE, parse_time('2026-10-13T04:30:00Z'))['workflows']['results']
        self.assertEqual(len(result['failures']), 1)
        self.assertNotIn('2026-10-13T04:17:00+01:00', result['missing_or_delayed_slots_local'])

    def test_pending_is_not_failure(self):
        rows = [run(SCANS['draw'][0], '2026-10-13T03:40:00Z', status='in_progress', conclusion='')]
        result = inspect(rows, DATE, parse_time('2026-10-13T04:50:00Z'))['workflows']['draw']
        self.assertEqual(result['unfinished'], ['1'])
        self.assertEqual(result['failures'], [])

    def test_incomplete_window_not_false_alarm(self):
        result = inspect([], DATE, parse_time('2026-10-13T03:30:00Z'))['workflows']['results']
        self.assertEqual(len(result['missing_or_delayed_slots_local']), 3)
        self.assertEqual(len(result['not_yet_evaluable_slots_local']), 1)

    def test_manual_run_not_counted(self):
        rows = [run(SCANS['results'][0], '2026-10-13T03:17:00Z', event='workflow_dispatch')]
        result = inspect(rows, DATE, parse_time('2026-10-13T04:30:00Z'))['workflows']['results']
        self.assertEqual(result['scheduled_runs'], 0)

    def test_csv_bom_and_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'runs.csv'
            path.write_text('1,"Scan FA Cup draw (guarded)","schedule","2026-10-13T03:37:00Z","2026-10-13T03:37:01Z","2026-10-13T03:38:00Z","completed","success","https://github.com/example"\n', encoding='utf-8-sig')
            self.assertEqual(read_csv(path)[0]['name'], SCANS['draw'][0])

if __name__ == '__main__':
    unittest.main()
