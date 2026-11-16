"""A definite host can be located before its replay-dependent visitor is known."""
import copy
import io
import json
import runpy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'updater'))
import enrich_replay_kickoffs_and_active_venues as enrich

GAZ = '<h3>Mansfield Town</h3><p>One Call Stadium</p><p>NG18 5DA</p>'


class ConditionalVenues(unittest.TestCase):
    def run_stage(self, stage, data, gaz=GAZ, grounds=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'competition.json'
            source.write_text(json.dumps(data))
            page = root / 'clubfinder.html'
            page.write_text('const GROUNDS=' + json.dumps(grounds or []) + ';')
            if stage == 'active':
                candidate = copy.deepcopy(data)
                with patch.object(enrich, 'HTML', page), patch.object(enrich, 'fetch', return_value=gaz):
                    enrich.enrich_active_venues(candidate)
                return candidate
            # Execute the unchanged CLI entrypoint in a disposable root. The
            # source network response is controlled; canonical input is not.
            (root / 'updater').mkdir()
            script = root / 'updater/enrich_later_round_venues.py'
            shutil.copyfile(ROOT / 'updater/enrich_later_round_venues.py', script)
            with patch('urllib.request.urlopen', return_value=io.BytesIO(gaz.encode())):
                runpy.run_path(str(script), run_name='__main__')
            return json.loads(source.read_text())

    def fixture(self, **changes):
        return dict(round='First Round Proper', date='2026-11-07', kickoff='15:00',
                    home='Mansfield Town', away='Macclesfield or Anstey N',
                    conditional=True, **changes)

    def test_definite_host_enriched_across_aliases_without_resolving_visitor(self):
        fixture = self.fixture()
        original = dict(fixtures={'Mansfield Town': copy.deepcopy(fixture), 'Anstey N': copy.deepcopy(fixture)},
                        result_history={'Earlier': [{'venue': {'postcode': 'M46 9EY'}}]})
        for stage in ('later', 'active'):
            with self.subTest(stage=stage):
                candidate = self.run_stage(stage, original)
                for row in candidate['fixtures'].values():
                    self.assertEqual(row['venue']['ground'], 'One Call Stadium')
                    self.assertEqual(row['venue']['postcode'], 'NG18 5DA')
                    self.assertEqual(row['venue']['source'], enrich.FCHD_URL)
                    self.assertEqual({k: v for k, v in row.items() if k != 'venue'}, fixture)
                self.assertEqual(candidate['result_history'], original['result_history'])
                self.assertEqual(self.run_stage(stage, candidate), candidate)
                self.assertNotIn('venue', original['fixtures']['Anstey N'])

    def test_conditional_host_unknown_source_and_existing_venue_are_protected(self):
        rows = [dict(self.fixture(), home='Mansfield Town or Other Town'),
                dict(self.fixture(), home='Unknown Club'),
                dict(self.fixture(), venue={'ground': 'Explicit Match Venue', 'postcode': 'AB1 2CD',
                                            'source': 'https://example.test/fixture'})]
        for stage in ('later', 'active'):
            for fixture in rows:
                data = dict(fixtures={'slot': fixture})
                with self.subTest(stage=stage, fixture=fixture):
                    self.assertEqual(self.run_stage(stage, data), data)

    def test_ambiguous_exact_source_is_not_replaced_by_a_looser_match(self):
        gaz = GAZ + '<h3>Mansfield Town</h3><p>Conflicting Ground</p><p>AB1 2CD</p>'
        gaz += '<h3>Mansfield Town Reserves</h3><p>Reserve Ground</p><p>XY1 2ZZ</p>'
        data = dict(fixtures={'slot': self.fixture()})
        for stage in ('later', 'active'):
            with self.subTest(stage=stage):
                self.assertEqual(self.run_stage(stage, data, gaz), data)

    def test_active_stage_uses_protected_ground_before_gazetteer(self):
        venue = dict(name='Mansfield Town', ground='Protected Ground', postcode='AA1 1AA',
                     source='https://example.test/protected')
        data = dict(fixtures={'slot': self.fixture()})
        candidate = self.run_stage('active', data, grounds=[venue])
        self.assertEqual(candidate['fixtures']['slot']['venue']['postcode'], 'AA1 1AA')
        self.assertEqual(candidate['fixtures']['slot']['venue']['source'], venue['source'])


if __name__ == '__main__':
    unittest.main()
