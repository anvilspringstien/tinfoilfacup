import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'updater'))
from import_draw_announcement import parse_announcement
from draw_ball_numbers import draw_schedule_at

class AnnouncementTests(unittest.TestCase):
    def setUp(self):
        self.raw = (ROOT / 'tests/fixtures/draw-announcement-first-proper.html').read_text()
        self.url = 'https://www.thefa.com/news/2026/oct/16/emirates-fa-cup-first-round-draw-to-be-broadcast-on-tnt-sports-20261610'
    def parse(self, **kwargs):
        args = dict(raw=self.raw, source_url=self.url, round_name='First Round Proper',
                    at='2026-10-19T18:35:00+01:00', expected_balls=80)
        args.update(kwargs)
        return parse_announcement(**args)
    def test_official_numbers(self):
        result = self.parse()
        self.assertEqual(result['ball_numbers']['AFC Fylde'], 64)
        self.assertEqual(len(result['ball_numbers']), 80)
        self.assertEqual(result['source_url'], self.url)
    def test_rejects_unconfirmed_metadata(self):
        for changes in [dict(source_url='https://example.com/'),
                        dict(round_name='Second Round Proper'),
                        dict(at='2026-10-20T18:35:00+01:00'),
                        dict(at='2026-10-19T19:35:00+01:00'),
                        dict(at='2026-10-19T18:35:00'),
                        dict(raw=self.raw.replace('<strong>64</strong>', '<strong>63</strong>'))]:
            with self.subTest(changes=list(changes)), self.assertRaises(ValueError):
                self.parse(**changes)

    def test_watcher_schedule_uses_season_weekday_and_london_timezone(self):
        for day, time, expected in [
            ('Monday 9 November', 'approximately 6.45pm GMT', '2026-11-09T18:45:00+00:00'),
            ('Monday 19 October', '6.35pm BST', '2026-10-19T18:35:00+01:00'),
            ('Monday 11 January', '7pm GMT', '2027-01-11T19:00:00+00:00'),
            ('Monday 9 November', '6.45pm BST', None),
            ('Tuesday 9 November', '6.45pm GMT', None),
            ('Monday 9 November', None, None),
        ]:
            with self.subTest(day=day, time=time):
                self.assertEqual(draw_schedule_at({'date_text': day, 'time_text': time}, '2026-27'), expected)


if __name__ == '__main__':
    unittest.main()
