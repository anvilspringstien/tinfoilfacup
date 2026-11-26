import unittest

from updater.apply_beta_current_ground_names import literal
from updater.publish_approved_public_club_records import reconcile, website_plan


class PublicClubFactsPublicationTests(unittest.TestCase):
    def test_only_approved_literals_can_change(self):
        original, updated, report = reconcile()

        def strip_reviewed_literals(html):
            ranges = [literal(html, name)[:2] for name in ('GROUNDS', 'LAW2_ORIGIN_LOCATIONS', 'CLUB_WEBSITES')]
            for left, right in sorted(ranges, reverse=True):
                html = html[:left] + html[right:]
            return html

        self.assertEqual(strip_reviewed_literals(original), strip_reviewed_literals(updated))
        for table in ('GROUNDS', 'LAW2_ORIGIN_LOCATIONS'):
            old = {row['name']: row for row in literal(original, table)[2]}
            new = {row['name']: row for row in literal(updated, table)[2]}
            self.assertEqual(old.keys(), new.keys())
            changed = {item['club'] for item in report['approved_ground_changes']}
            self.assertTrue(all(old[name] == new[name] or name in changed for name in old))
            self.assertTrue(all(not row.get('preview_evidence_only') for row in new.values()))
        self.assertEqual(report['public_after']['eligible'], report['public_before']['eligible'])

    def test_preserves_conflicts_and_unapproved_candidates(self):
        public = {'Conflict FC': 'https://already.example/'}
        beta = {'Conflict FC': 'https://another.example/', 'Unreviewed FC': 'https://guess.example/',
                'Approved FC': 'https://approved.example/', 'Withdrawn FC': 'https://withdrawn.example/'}
        evidence = {
            name: ({'club': name, 'url': beta[name], 'status': status}, 'test-ledger.json')
            for name, status in [('Conflict FC', 'verified_official_club_site'),
                                 ('Approved FC', 'verified_official_club_site'),
                                 ('Withdrawn FC', 'club_confirmed_offline')]
        }
        ready, held = website_plan(public, beta, evidence)
        self.assertEqual([row['club'] for row, _ in ready], ['Approved FC'])
        self.assertEqual({h['identity']: h['reason'] for h in held}, {
            'Conflict FC': 'conflicting_public_mapping',
            'Unreviewed FC': 'missing_current_approval',
            'Withdrawn FC': 'missing_current_approval',
        })
