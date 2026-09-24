import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "updater"))
from discover_quarantined_replay_urls import discover, approved_host, fixture_query

FIXTURE = {"home": "Weston-super-Mare", "away": "Wimborne Town",
           "date": "2026-09-22", "reason": "penalty decision with non-level source score"}


class DiscoveryTests(unittest.TestCase):
    def test_fa_bbc_clubs_regional_priority(self):
        calls = []
        def search(query, domain):
            calls.append(domain)
            return ["https://" + domain + "/fixture/replay"]
        result = discover(FIXTURE, ["wsmafc.co.uk", "wimbornetownfc.co.uk"],
                          ["southwestsportsnews.com"], search)
        self.assertEqual(calls, ["thefa.com", "bbc.co.uk", "wsmafc.co.uk",
                                 "wimbornetownfc.co.uk", "southwestsportsnews.com"])
        self.assertEqual(len(result["sources"]), 5)
        self.assertFalse(result["production_mutation"])

    def test_no_trust_in_search_result_domains(self):
        def search(query, domain):
            return ["https://thefa.com.evil.test/fake", "http://" + domain + "/insecure",
                    "https://" + domain + "/real"]
        result = discover(FIXTURE, search=search, regional_domains=())
        self.assertEqual([x["url"] for x in result["sources"]],
                         ["https://thefa.com/real", "https://bbc.co.uk/real"])

    def test_missing_bbc_does_not_stop_fallback(self):
        def search(query, domain):
            if domain == "bbc.co.uk":
                raise TimeoutError()
            return ["https://" + domain + "/report"]
        result = discover(FIXTURE, ["wimbornetownfc.co.uk"], (), search)
        self.assertEqual(result["failures"][0]["domain"], "bbc.co.uk")
        self.assertEqual(len(result["sources"]), 2)

    def test_wikipedia_and_fwp_cannot_confirm(self):
        result = discover(FIXTURE, ["wikipedia.org", "footballwebpages.co.uk"], (),
                          lambda q, d: ["https://" + d + "/fixture"])
        self.assertEqual(len(result["sources"]), 2)

    def test_query_is_fixture_specific(self):
        query = fixture_query(FIXTURE)
        self.assertIn("Wimborne Town", query)
        self.assertIn("22 September 2026", query)

    def test_reject_embedded_credentials(self):
        self.assertFalse(approved_host("https://user:pass@bbc.co.uk/fixture", "bbc.co.uk"))


if __name__ == "__main__":
    unittest.main()
