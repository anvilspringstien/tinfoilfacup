"""Offline ingestion and historical metadata checks using captured source HTML."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'updater'))
import auto_round_results as scan
import enrich_replay_kickoffs_and_active_venues as enrich
from result_metadata import preserve_result_metadata, retain_metadata
import sync_active_replay_fixtures as sync

FIXTURES = ROOT / 'tests/fixtures/results-repair'
REPLAY_URL = 'https://www.footballwebpages.co.uk/match/2026-2027/emirates-fa-cup/atherton-collieries/trafford/594362'


def source_fetch(url):
    if url.endswith('/20261006'):
        return (FIXTURES / '20261006.html').read_text()
    if url == REPLAY_URL:
        return (FIXTURES / 'atherton-trafford.html').read_text()
    return ''


def replay_result():
    return {'home': 'Atherton Collieries', 'away': 'Trafford', 'date': '2026-10-06',
            'round': 'Third Round Qualifying Replay', 'home_score': 3, 'away_score': 0,
            'status': 'FT', 'winner': 'Atherton Collieries', 'decision': '',
            'source_url': scan.fwp_round_url('Third Round Qualifying') + '-replay'}


class ResultsRepair(unittest.TestCase):
    def fixture(self):
        r = replay_result()
        return {**{k: r[k] for k in ('home', 'away', 'date', 'round', 'source_url')},
                'kickoff': '19:45', 'venue': {'ground': 'Dreams2Remember Stadium',
                'postcode': 'M46 9EY', 'source': 'https://example.test/verified-fixture'}}

    def test_import_retains_exact_replay_metadata_across_all_aliases(self):
        d = {'replays': {'Atherton Collieries': self.fixture()}}
        self.assertTrue(scan.merge_result(d, replay_result()))
        for rows in d['result_history'].values():
            self.assertEqual(rows[0]['kickoff'], '19:45')
            self.assertEqual(rows[0]['venue']['postcode'], 'M46 9EY')
            self.assertEqual(rows[0]['home_score'], 3)
            self.assertEqual(rows[0]['date'], '2026-10-06')
        self.assertFalse(scan.merge_result(d, replay_result()))

    def test_transfer_before_completed_pending_replay_is_pruned(self):
        r = replay_result()
        d = {'replays': {'Atherton Collieries': self.fixture()},
             'results': {'Atherton Collieries': copy.deepcopy(r)},
             'result_history': {'Atherton Collieries': [copy.deepcopy(r)]}}
        self.assertEqual(preserve_result_metadata(d), 2)
        pending, _ = sync.resolve(d, [])
        self.assertEqual(pending, {})
        d['replays'] = pending
        self.assertEqual(d['result_history']['Atherton Collieries'][0]['kickoff'], '19:45')
        self.assertEqual(preserve_result_metadata(d), 0)

    def test_other_date_round_and_reversed_home_venue_never_leak(self):
        for change in ({'date': '2026-10-03'}, {'round': 'Third Round Qualifying'},
                       {'home': 'Trafford', 'away': 'Atherton Collieries'}):
            with self.subTest(change=change):
                r = retain_metadata(replay_result(), [{**self.fixture(), **change}])
                self.assertNotIn('kickoff', r)
                self.assertNotIn('venue', r)

    def test_conflicting_populated_metadata_fails_closed(self):
        for change in ({'kickoff': '20:00'}, {'venue': {'postcode': 'M41 5DL', 'source': 'https://example.test/conflict'}}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                retain_metadata({**replay_result(), **self.fixture()}, [{**self.fixture(), **change}])

    def test_tbc_is_missing_and_unsourced_metadata_is_not_copied(self):
        r = retain_metadata({**replay_result(), 'kickoff': 'Kick-off TBC'}, [self.fixture()])
        self.assertEqual(r['kickoff'], '19:45')
        f = self.fixture(); f.pop('source_url'); f.pop('venue')
        self.assertNotIn('kickoff', retain_metadata(replay_result(), [f]))

    def test_third_qualifying_match_page_recovers_1945_with_provenance(self):
        r = replay_result()
        source_text = enrich.clean_text((FIXTURES / 'atherton-trafford.html').read_text())
        self.assertIn('Full-time: Atherton Collieries 3-0 Trafford', source_text)
        with patch.object(enrich, 'fetch', side_effect=source_fetch):
            details, count = enrich.replay_source_details([r])
        self.assertGreater(count, 0)
        self.assertEqual(details[enrich.replay_identity(r)], (REPLAY_URL, '19:45'))
        d = {'results': {'Atherton': copy.deepcopy(r)}, 'result_history': {'Trafford': [copy.deepcopy(r)]}}
        self.assertEqual(enrich.apply_replay_kickoffs(d, details), 2)
        self.assertEqual(d['result_history']['Trafford'][0]['kickoff_source_url'], REPLAY_URL)

    def test_wrong_date_round_or_orientation_cannot_supply_kickoff(self):
        for change in ({'date': '2026-10-07'}, {'round': 'Second Round Qualifying Replay'},
                       {'home': 'Trafford', 'away': 'Atherton Collieries'}):
            with self.subTest(change=change), patch.object(enrich, 'fetch', side_effect=source_fetch):
                details, _ = enrich.replay_source_details([{**replay_result(), **change}])
                self.assertEqual(details, {})

    def test_full_replay_round_label_exception_requires_existing_reviewed_evidence(self):
        ledger = json.loads((ROOT / 'updater/exceptional-replay-dispositions.json').read_text())
        row = next(x['replay_result'] for x in ledger['dispositions'] if 'Mulbarton' in str(x))
        self.assertIn('second qualifying round', enrich.source_round_labels(row))
        self.assertNotIn('second qualifying round', enrich.source_round_labels({**row, 'date': '2026-09-30'}))
        self.assertNotIn('second qualifying round', enrich.source_round_labels({**row, 'home_score': 9}))

    def test_captured_fylde_full_time_result_is_classified_not_inferred(self):
        data = json.loads((ROOT / 'competition.json').read_text())
        rnd, known = scan.active_fixtures(data)
        raw = (FIXTURES / 'fourth-qualifying-round.html').read_text()
        scan.validate_fwp_round_page(raw, rnd, scan.fwp_round_url(rnd))
        rows = scan.parse_fwp_observations(raw, known, scan.fwp_round_url(rnd))
        row = next(x for x in rows if x['observation']['home'] == 'AFC Fylde')
        out = scan.classify_observation(row['fixture'], row['observation'], scan.history_rows(data))
        self.assertEqual(out['kind'], 'result')
        self.assertEqual((out['result']['home_score'], out['result']['away_score'], out['result']['status']), (5, 0, 'FT'))
        self.assertEqual(out['result']['winner'], 'AFC Fylde')
        verified = json.loads((FIXTURES / 'verified-milestones.json').read_text())
        self.assertEqual(out['result'], verified['fylde'])
        for status in ('HT', 'LIVE', ''):
            with self.subTest(status=status), self.assertRaises(ValueError):
                scan.classify_observation(row['fixture'], {**row['observation'], 'status': status}, [])


if __name__ == '__main__':
    unittest.main()
