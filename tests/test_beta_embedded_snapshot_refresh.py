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
        self.live = {
            'schema_version': 1, 'updated_at': '2026-09-24T10:00:00Z',
            'result_history': {'Thame United': [{'winner': 'Thame United'}]},
            'fixtures': {'Thame Utd': {'home': 'Thame Utd or Exmouth Town'}},
        }
        self.html = BETA.read_text(encoding='utf-8')

    def test_refresh_is_idempotent_and_does_not_edit_html(self):
        expected = json.dumps(self.live, ensure_ascii=False, separators=(',', ':')) + '\n'
        self.assertEqual(refresh(self.html, self.live), expected)
        self.assertEqual(refresh(self.html, self.live), expected)

    def test_changed_loader_boundary_fails_closed(self):
        for old, new in (
            ("../competition.json", "./competition.json"),
            ("./competition-fallback.json", "../competition.json"),
            ("loadSource(BETA_COMPETITION_DATA_URL", "loadSource('missing.json'"),
            ("loadSource(PRODUCTION_COMPETITION_DATA_URL", "loadSource('missing.json'"),
        ):
            with self.subTest(old=old):
                with self.assertRaises(ValueError):
                    refresh(self.html.replace(old, new), self.live)

    def test_reversed_source_precedence_fails_closed(self):
        canonical = "const d=await loadSource(PRODUCTION_COMPETITION_DATA_URL,'canonical');"
        fallback = "const d=await loadSource(BETA_COMPETITION_DATA_URL,'BETA fallback');"
        changed = self.html.replace(canonical, '__CANONICAL__').replace(fallback, canonical).replace('__CANONICAL__', fallback)
        with self.assertRaises(ValueError):
            refresh(changed, self.live)

    def test_refresh_source_is_canonical_competition(self):
        self.assertEqual(DATA, ROOT / 'competition.json')
        self.assertNotEqual(DATA, ROOT / 'beta' / 'competition.json')

    def test_committed_fallback_matches_canonical_data(self):
        live = json.loads(DATA.read_text(encoding='utf-8'))
        self.assertIn("const PRODUCTION_COMPETITION_DATA_URL='../competition.json';", self.html)
        self.assertNotIn("const PRODUCTION_COMPETITION_DATA_URL='./competition.json';", self.html)
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
        archived = fallback.get('round_fixtures', {}).get('Third Round Qualifying', [])
        archived_rows = archived if isinstance(archived, list) else archived.values()
        self.assertTrue(any(
            v.get('round') == 'Third Round Qualifying'
            and v.get('home') == 'Thame United'
            and v.get('away') == 'Eastbourne Borough'
            for v in archived_rows))
        active_fqr = {
            (v.get('round'), v.get('date'), v.get('home'), v.get('away'))
            for v in fallback.get('fixtures', {}).values()
            if v.get('round') == 'Fourth Round Qualifying'
        }
        self.assertEqual(len(active_fqr), 32)


if __name__ == '__main__':
    unittest.main()
