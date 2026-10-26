import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'updater'))
from apply_beta_current_ground_names import apply_names, literal


class CurrentGroundNameTests(unittest.TestCase):
    def setUp(self):
        self.ledger = json.loads((ROOT / 'updater/current-ground-name-ledger.json').read_text())
        self.row = {'name': 'Sholing FC', 'ground': 'Mortgage Decisions Community Stadium', 'postcode': 'SO19 9PW', 'lat': 50.893288, 'lon': -1.338082, 'source': 'original provenance'}
        self.html = 'BEFORE const ELIGIBLE=[{"name":"Sholing FC"}];let GROUNDS=' + json.dumps([self.row], separators=(',', ':')) + ';AFTER'

    def test_only_ground_name_changes_and_repeat_is_noop(self):
        updated, changes = apply_names(self.html, self.ledger)
        self.assertEqual(changes, ['Sholing FC'])
        self.assertEqual(literal(updated, 'GROUNDS')[2], [dict(self.row, ground='The Charters Stadium')])
        self.assertEqual(updated, self.html.replace('Mortgage Decisions Community Stadium', 'The Charters Stadium'))
        self.assertEqual(apply_names(updated, self.ledger), (updated, []))

    def test_unknown_duplicate_or_unreviewed_club_fails(self):
        for change in ({'club': 'Another FC'}, {'status': 'candidate'}, {'public_sources': []}):
            ledger = copy.deepcopy(self.ledger)
            ledger['approved'][0].update(change)
            with self.assertRaises(ValueError):
                apply_names(self.html, ledger)
        ledger = copy.deepcopy(self.ledger)
        ledger['approved'] *= 2
        with self.assertRaises(ValueError):
            apply_names(self.html, ledger)

    def test_postcode_or_unexpected_name_drift_fails(self):
        for original, replacement in (('SO19 9PW', 'SO19 9PX'), ('Mortgage Decisions Community Stadium', 'Unexpected ground')):
            with self.assertRaises(ValueError):
                apply_names(self.html.replace(original, replacement), self.ledger)

    def test_committed_listing_matches_reviewed_name(self):
        html = (ROOT / 'beta/clubfinder-beta.html').read_text()
        self.assertEqual(apply_names(html, self.ledger), (html, []))


if __name__ == '__main__':
    unittest.main()
