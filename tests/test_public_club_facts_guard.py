import unittest
from pathlib import Path

from updater.public_club_facts_guard import prove, website_plan

ROOT = Path(__file__).resolve().parents[1]


class PublicClubFactsGuardTests(unittest.TestCase):
    def test_rejects_non_factual_changes_and_unapproved_ground_rows(self):
        original = 'const GROUNDS=[{"name":"Test FC","ground":"Ground"}];const LAW2_ORIGIN_LOCATIONS=[];const CLUB_WEBSITES={};'
        for new in (original + '/* UI change */', original.replace('"ground":"Ground"', '"ground":"New Ground"'),
                    original.replace('"name":"Test FC"', '"name":"Another FC"'),
                    original.replace('WEBSITES={}', 'WEBSITES={"Test FC":"https://unreviewed.example/"}')):
            with self.assertRaises(ValueError):
                prove(ROOT, original, new, new, {'approved': []}, {})

    def test_rejects_replacing_existing_public_website(self):
        original = 'const CLUB_WEBSITES={"Test FC":"https://current.example/"};'
        with self.assertRaisesRegex(ValueError, 'replacement or removal'):
            prove(ROOT, original, original.replace('current', 'replacement'), original, {}, {})

    def test_website_plan_uses_exact_identity_and_current_approval(self):
        beta = {'Test FC': 'https://test.example/', 'Test Town FC': 'https://test-town.example/'}
        evidence = {'Test FC': ({'club': 'Test FC', 'status': 'verified_official_club_site',
                                 'url': beta['Test FC']}, 'test-ledger.json')}
        additions, held = website_plan({}, beta, evidence)
        self.assertEqual([item['club'] for item, _ in additions], ['Test FC'])
        self.assertEqual([item['identity'] for item in held], ['Test Town FC'])
