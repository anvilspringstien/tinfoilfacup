from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "updater"))

import sync_active_replay_fixtures as sync


class ActiveReplayFixtureSyncRegression(unittest.TestCase):
    def sample_data(self):
        weston_draw = {
            "home": "Weston-super-Mare",
            "away": "Wimborne Town",
            "home_score": 1,
            "away_score": 1,
            "winner": "",
            "status": "FT",
            "decision": "draw-replay",
            "date": "2026-09-19",
            "round": "Second Round Qualifying",
        }
        old_draw = {
            "home": "Wimborne Town",
            "away": "Portishead Town",
            "home_score": 0,
            "away_score": 0,
            "winner": "",
            "status": "FT",
            "decision": "draw-replay",
            "date": "2026-09-05",
            "round": "First Round Qualifying",
        }
        old_replay = {
            "home": "Portishead Town",
            "away": "Wimborne Town",
            "home_score": 1,
            "away_score": 3,
            "winner": "Wimborne Town",
            "status": "AET",
            "decision": "aet",
            "date": "2026-09-08",
            "round": "First Round Qualifying Replay",
        }
        return {
            "results": {},
            "replays": {},
            "result_history": {
                "Weston-super-Mare": [weston_draw],
                "Wimborne Town": [old_draw, old_replay, weston_draw],
                "Portishead Town": [old_draw, old_replay],
            },
        }

    def test_only_unresolved_draw_is_pending(self):
        rows = sync.unresolved_draws(self.sample_data())
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["home"], "Weston-super-Mare")
        self.assertEqual(rows[0]["away"], "Wimborne Town")
        self.assertEqual(rows[0]["round"], "Second Round Qualifying")

    def test_parses_replay_schedule_date_orientation_and_kickoff(self):
        html = """
        <html><body>
          <h3>Tuesday 22nd September 2026</h3>
          <table>
            <tr><td>7.45pm</td><td>Wimborne Town</td><td>v</td><td>Weston-super-Mare</td></tr>
          </table>
        </body></html>
        """
        rows = sync.parse_source_fixtures(html, "https://example.test/fa-cup")
        self.assertEqual(
            rows,
            [{
                "home": "Wimborne Town",
                "away": "Weston-super-Mare",
                "date": "2026-09-22",
                "kickoff": "19:45",
                "source_url": "https://example.test/fa-cup",
            }],
        )

    def test_proven_draw_can_create_replay_fixture_but_unrelated_row_cannot(self):
        source = [
            {
                "home": "Wimborne Town",
                "away": "Weston-super-Mare",
                "date": "2026-09-22",
                "kickoff": "19:45",
                "source_url": sync.SOURCE_URL,
            },
            {
                "home": "Unrelated Town",
                "away": "Another City",
                "date": "2026-09-22",
                "kickoff": "19:45",
                "source_url": sync.SOURCE_URL,
            },
        ]
        replay_map, details = sync.resolve(self.sample_data(), source)
        self.assertEqual(details["unresolved_draws"], 1)
        self.assertEqual(details["discovered_replays"], 1)
        self.assertEqual(details["unique_replay_fixtures"], 1)
        self.assertEqual(details["awaiting_fixture_details"], [])
        fixture = replay_map["Weston-super-Mare"]
        self.assertEqual(fixture["round"], "Second Round Qualifying Replay")
        self.assertEqual(fixture["home"], "Wimborne Town")
        self.assertEqual(fixture["away"], "Weston-super-Mare")
        self.assertEqual(fixture["date"], "2026-09-22")
        self.assertEqual(fixture["kickoff"], "19:45")
        self.assertIn("Weston-super-Mare FC", replay_map)
        self.assertIn("Wimborne Town FC", replay_map)
        self.assertNotIn("Unrelated Town", replay_map)

    def test_existing_fixture_is_retained_if_source_temporarily_omits_it(self):
        data = self.sample_data()
        data["replays"] = {
            "Weston-super-Mare": {
                "round": "Second Round Qualifying Replay",
                "home": "Wimborne Town",
                "away": "Weston-super-Mare",
                "date": "2026-09-22",
                "kickoff": "19:45",
                "source_url": sync.SOURCE_URL,
            }
        }
        replay_map, details = sync.resolve(data, [])
        self.assertEqual(details["discovered_replays"], 0)
        self.assertEqual(details["retained_existing_replays"], 1)
        self.assertEqual(details["unique_replay_fixtures"], 1)
        self.assertEqual(replay_map["Wimborne Town"]["date"], "2026-09-22")

    def test_terminal_replay_prunes_pending_fixture(self):
        data = self.sample_data()
        completed = {
            "home": "Wimborne Town",
            "away": "Weston-super-Mare",
            "home_score": 2,
            "away_score": 0,
            "winner": "Wimborne Town",
            "status": "FT",
            "decision": "",
            "date": "2026-09-22",
            "round": "Second Round Qualifying Replay",
        }
        data["result_history"]["Wimborne Town"].append(completed)
        data["result_history"]["Weston-super-Mare"].append(completed)
        data["replays"] = {
            "Wimborne Town": {
                "round": "Second Round Qualifying Replay",
                "home": "Wimborne Town",
                "away": "Weston-super-Mare",
                "date": "2026-09-22",
                "kickoff": "19:45",
            }
        }
        replay_map, details = sync.resolve(data, [])
        self.assertEqual(details["unresolved_draws"], 0)
        self.assertEqual(replay_map, {})


if __name__ == "__main__":
    unittest.main()
