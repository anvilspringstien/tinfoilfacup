"""BETA's offline competition snapshot must match validated live data exactly."""
import json
import re
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "updater"))
from refresh_beta_embedded_snapshot import refresh, BEGIN, END, BETA, DATA


def sample_html(payload):
    return (
        "const LIVE_COMPETITION_DATA_URL='../competition.json';\n"
        + BEGIN + "\nconst EMBEDDED_COMPETITION_DATA="
        + json.dumps(payload, separators=(",", ":")) + ";\n" + END + "\n"
        + "let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;\n"
        + "async function refreshCompetitionData(){"
        + "catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;"
        + "applyLiveRoundDates();}}\n"
    )


class BetaEmbeddedSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.canonical = {
            "schema_version": 1, "updated_at": "2026-09-24T10:00:00Z",
            "result_history": {"Thame United": [{"winner": "Thame United"}]},
            "fixtures": {"Thame Utd": {"home": "Thame Utd or Exmouth Town"}},
        }

    def test_refresh_only_replaces_snapshot_and_is_idempotent(self):
        original = "prefix\n" + sample_html({"old": True}) + "\nsuffix\n"
        refreshed = refresh(original, self.canonical)
        self.assertNotEqual(original, refreshed)
        self.assertEqual(refresh(refreshed, self.canonical), refreshed)
        self.assertEqual(refreshed.split(BEGIN)[0], original.split(BEGIN)[0])
        self.assertEqual(refreshed.split(END)[1], original.split(END)[1])
        payload = re.search(
            r"const EMBEDDED_COMPETITION_DATA=(.*?);\n" + re.escape(END),
            refreshed, re.S)
        self.assertIsNotNone(payload)
        self.assertEqual(json.loads(payload.group(1)), self.canonical)

    def test_missing_or_changed_fallback_boundaries_fail_closed(self):
        example = sample_html({"old": True})
        for broken in (
            example.replace(END, ""),
            example.replace("../competition.json", "./competition.json"),
            example.replace("applyLiveRoundDates();", ""),
            example.replace(BEGIN, BEGIN + BEGIN),
        ):
            with self.subTest(broken=broken[-60:]):
                with self.assertRaises(ValueError):
                    refresh(broken, self.canonical)

    def test_committed_beta_snapshot_matches_canonical_result(self):
        live = json.loads(DATA.read_text(encoding="utf-8"))
        html = BETA.read_text(encoding="utf-8")
        self.assertEqual(html, refresh(html, live),
                         "BETA fallback is older than canonical competition.json")
        marker = re.search(
            r"const EMBEDDED_COMPETITION_DATA=(.*?);\n" + re.escape(END),
            html, re.S)
        self.assertIsNotNone(marker)
        embedded = json.loads(marker.group(1))
        self.assertEqual(embedded, live)
        self.assertTrue(any(
            r.get("round") == "Second Round Qualifying Replay"
            and r.get("home") == "Exmouth Town"
            and r.get("away") == "Thame United"
            and r.get("winner") == "Thame United"
            and r.get("home_score") == 1 and r.get("away_score") == 3
            for r in embedded.get("results", {}).values()
        ), "Published Exmouth–Thame replay missing from offline fallback")
        self.assertTrue(any(
            v.get("round") == "Third Round Qualifying"
            and v.get("home") == "Thame Utd or Exmouth Town"
            and v.get("away") == "Eastbourne Borough"
            for v in embedded.get("fixtures", {}).values()
        ), "Published next-round conditional draw missing from BETA fallback")


if __name__ == "__main__":
    unittest.main()
