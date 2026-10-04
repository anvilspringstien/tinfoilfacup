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

    def test_future_round_unfamiliar_state_reaches_fallback_exactly(self):
        future = {
            'schema_version': 1,
            'updated_at': '2099-10-10T22:17:00Z',
            'source_round': 'Fourth Round Qualifying',
            'result_history': {
                'Pigeon Vale': [{
                    'round': 'Fourth Round Qualifying',
                    'date': '2099-10-10',
                    'home': 'Pigeon Vale',
                    'away': 'Anvil Rovers',
                    'home_score': 3,
                    'away_score': 1,
                    'winner': 'Pigeon Vale',
                    'status': 'FT',
                    'venue': {
                        'ground': 'The Great Deterministic Boundary',
                        'postcode': 'ZZ1 1ZZ',
                        'verification': 'verified',
                    },
                }],
            },
            'results': {
                'Pigeon Vale': {
                    'round': 'Fourth Round Qualifying',
                    'home': 'Pigeon Vale',
                    'away': 'Anvil Rovers',
                    'winner': 'Pigeon Vale',
                },
            },
            'fixtures': {
                'future-wednesday-v-pigeon-vale': {
                    'round': 'First Round Proper',
                    'date': '2099-11-07',
                    'home': 'Future Wednesday',
                    'away': 'Pigeon Vale',
                    'venue': {
                        'ground': 'Tomorrow Stadium',
                        'postcode': 'YY1 1YY',
                        'verification': 'verified',
                    },
                },
            },
        }
        rendered = refresh(self.html, future)
        propagated = json.loads(rendered)
        self.assertEqual(propagated, future)
        self.assertEqual(propagated['updated_at'], future['updated_at'])
        self.assertEqual(
            propagated['result_history']['Pigeon Vale'][0]['venue']['postcode'],
            'ZZ1 1ZZ',
        )
        self.assertEqual(
            propagated['fixtures']['future-wednesday-v-pigeon-vale']['venue']['postcode'],
            'YY1 1YY',
        )
        self.assertNotIn('Thame United', rendered)
        self.assertNotIn('Eastbourne Borough', rendered)

    def test_changed_loader_boundary_fails_closed(self):
        for old, new in (
            ("../competition.json", "./competition.json"),
            ("./competition-fallback.json", "../competition.json"),
            ("fetch(FALLBACK_COMPETITION_DATA_URL", "fetch('missing.json'"),
        ):
            with self.subTest(old=old):
                with self.assertRaises(ValueError):
                    refresh(self.html.replace(old, new), self.live)

    def test_refresh_source_is_canonical_competition(self):
        self.assertEqual(DATA, ROOT / 'competition.json')
        self.assertNotEqual(DATA, ROOT / 'beta' / 'competition.json')

    def test_committed_fallback_matches_canonical_data(self):
        live = json.loads(DATA.read_text(encoding='utf-8'))
        self.assertIn("const LIVE_COMPETITION_DATA_URL='../competition.json';", self.html)
        self.assertNotIn("const LIVE_COMPETITION_DATA_URL='./competition.json';", self.html)
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
            and v.get('away') == 'Eastbourne Borough'
            for v in fallback.get('fixtures', {}).values()))


if __name__ == '__main__':
    unittest.main()
