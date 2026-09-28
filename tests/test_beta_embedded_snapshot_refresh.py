"""BETA's separate fallback remains an exact copy of canonical competition data."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'updater'))
from refresh_beta_embedded_snapshot import refresh, BETA, DATA, FALLBACK


class BetaFallbackSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.canonical = {
            'schema_version': 1, 'updated_at': '2026-09-24T10:00:00Z',
            'result_history': {'Thame United': [{'winner': 'Thame United'}]},
            'fixtures': {'Thame Utd': {'home': 'Thame Utd or Exmouth Town'}},
        }
        self.html = BETA.read_text(encoding='utf-8')

    def test_refresh_is_idempotent_and_does_not_edit_html(self):
        expected = json.dumps(self.canonical, ensure_ascii=False, separators=(',', ':')) + '\n'
        self.assertEqual(refresh(self.html, self.canonical), expected)
        self.assertEqual(refresh(self.html, self.canonical), expected)

    def test_changed_loader_boundary_fails_closed(self):
        for old, new in (
            ("../competition.json", "./competition.json"),
            ("./competition-fallback.json", "../competition.json"),
            ("fetch(FALLBACK_COMPETITION_DATA_URL", "fetch('missing.json'"),
        ):
            with self.subTest(old=old):
                with self.assertRaises(ValueError):
                    refresh(self.html.replace(old, new), self.canonical)

    def test_committed_fallback_matches_canonical(self):
        live = json.loads(DATA.read_text(encoding='utf-8'))
        fallback = json.loads(FALLBACK.read_text(encoding='utf-8'))
        self.assertEqual(FALLBACK.read_text(encoding='utf-8'), refresh(self.html, live))
        self.assertEqual(fallback, live)
        self.assertTrue(any(
            r.get('round') == 'Second Round Qualifying Replay'
            and r.get('home') == 'Exmouth Town'
            and r.get('away') == 'Thame United'
            and r.get('winner') == 'Thame United'
            and r.get('home_score') == 1 and r.get('away_score') == 3
            for r in fallback.get('results', {}).values()))
        self.assertTrue(any(
            v.get('round') == 'Third Round Qualifying'
            and v.get('home') == 'Thame Utd or Exmouth Town'
            and v.get('away') == 'Eastbourne Borough'
            for v in fallback.get('fixtures', {}).values()))


if __name__ == '__main__':
    unittest.main()
