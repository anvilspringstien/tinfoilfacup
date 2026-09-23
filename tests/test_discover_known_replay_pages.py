import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "updater"))
from discover_known_replay_pages import discover_known_pages, FA_FIXTURES, FA_RESULTS, BBC_MONTH

FIXTURE = {"home": "Wimborne Town", "away": "Weston Super Mare",
           "date": "2026-09-22", "reason": "penalty decision with non-level source score"}
HTML = '<html><body>Wimborne Town v Weston Super Mare 22 September 2026 <a href="/competitions/thefacup/match/68R">Wimborne Town</a></body></html>'


class KnownPageTests(unittest.TestCase):
    def test_known_fa_bbc_pages_need_no_key(self):
        calls = []
        def get(url):
            calls.append(url)
            return HTML
        rows = discover_known_pages(FIXTURE, get)
        self.assertEqual(calls, [FA_FIXTURES, FA_RESULTS,
                                 BBC_MONTH.format(month="2026-09")])
        self.assertEqual(len([x for x in rows["sources"] if x["tier"] == "fa"]), 4)
        self.assertFalse(rows["production_mutation"])

    def test_absent_fixture_fails_closed(self):
        rows = discover_known_pages(FIXTURE, lambda url: "<p>Other clubs only</p>")
        self.assertEqual(rows["sources"], [])
        self.assertEqual(len(rows["failures"]), 3)

    def test_unavailable_bbc_does_not_block_fa(self):
        def get(url):
            if "bbc.co.uk" in url:
                raise TimeoutError()
            return HTML
        rows = discover_known_pages(FIXTURE, get)
        self.assertTrue(rows["sources"])
        self.assertEqual(rows["failures"][0]["reason"], "TimeoutError")

    def test_no_off_domain_links(self):
        html = HTML.replace("</body>", '<a href="https://evil.test/fixture">Wimborne Town</a></body>')
        rows = discover_known_pages(FIXTURE, lambda url: html)
        self.assertFalse(any("evil.test" in x["url"] for x in rows["sources"]))


if __name__ == "__main__":
    unittest.main()
