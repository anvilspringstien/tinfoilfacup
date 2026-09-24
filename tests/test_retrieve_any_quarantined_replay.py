import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "updater"))
from retrieve_any_quarantined_replay import extract, retrieve, normalise

FIXTURE = {"home": "Example Town", "away": "United AFC", "date": "2026-09-22",
           "reason": "penalty decision with non-level source score: independent verification required"}
SOURCES = [
    {"domain": "exampletownfc.co.uk", "url": "https://exampletownfc.co.uk/report"},
    {"domain": "independentnews.co.uk", "url": "https://independentnews.co.uk/replay"},
]
KEY = FIXTURE["date"] + "|" + normalise(FIXTURE["home"]) + "|" + normalise(FIXTURE["away"])
HTML = "<p>FA Cup Replay 22 September 2026 Example Town 1-1 United AFC after extra time. Example Town won 4-3 on penalties.</p>"

class GenericRetrievalTests(unittest.TestCase):
    def test_arbitrary_fixture_with_two_publishers(self):
        pages = {s["url"]: HTML for s in SOURCES}
        rows = retrieve([FIXTURE], {KEY: SOURCES}, lambda url: pages[url])
        self.assertEqual(rows[0]["reconciliation"]["status"], "independently_verified", rows[0])
        self.assertFalse(rows[0]["production_mutation"])
    def test_opponent_in_scoreline_cannot_be_mistaken_for_penalty_winner(self):
        evidence = extract(FIXTURE, SOURCES[0], HTML)
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence["winner"], "Example Town")
        self.assertEqual((evidence["home_pens"], evidence["away_pens"]), (4, 3))

    def test_missing_second_publisher_quarantines(self):
        rows = retrieve([FIXTURE], {KEY: SOURCES[:1]}, lambda url: HTML)
        self.assertEqual(rows[0]["reconciliation"]["status"], "quarantined")
    def test_wrong_date_rejected(self):
        self.assertIsNone(extract(FIXTURE, SOURCES[0], HTML.replace("22 September", "19 September")))
    def test_wrong_clubs_rejected(self):
        self.assertIsNone(extract(FIXTURE, SOURCES[0], HTML.replace("United AFC", "Other AFC")))
    def test_unreviewed_domain_rejected(self):
        self.assertIsNone(extract(FIXTURE, SOURCES[0], HTML.replace("Example Town", "Example Town")) if False else
                          extract(FIXTURE, dict(SOURCES[0], url="https://imposter.example/report"), HTML))
    def test_conflicting_penalty_scores_quarantined(self):
        pages = {SOURCES[0]["url"]: HTML, SOURCES[1]["url"]: HTML.replace("4-3", "5-4")}
        rows = retrieve([FIXTURE], {KEY: SOURCES}, lambda url: pages[url])
        self.assertEqual(rows[0]["reconciliation"]["status"], "quarantined")
    def test_unavailable_publisher_quarantined(self):
        def fetch(url):
            if url == SOURCES[1]["url"]:
                raise TimeoutError()
            return HTML
        rows = retrieve([FIXTURE], {KEY: SOURCES}, fetch)
        self.assertEqual(rows[0]["reconciliation"]["status"], "quarantined")
        self.assertEqual(len(rows[0]["failures"]), 1, rows[0])

if __name__ == "__main__":
    unittest.main()
