import unittest
from pathlib import Path

from updater.public_club_facts_guard import prove, reviewed_websites, website_plan

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

    def test_trafford_warning_permits_only_matching_withdrawal_in_both_builds(self):
        original = (
            'const ELIGIBLE=[{"name":"Trafford FC"}];'
            'const GROUNDS=[];const LAW2_ORIGIN_LOCATIONS=[];'
            'const CLUB_WEBSITES={"Trafford":"https://traffordfc.com/",'
            '"Trafford FC":"https://traffordfc.com/","Other":"https://other.example/"};'
        )
        proposed = original.replace('"Trafford":"https://traffordfc.com/",', '').replace(
            '"Trafford FC":"https://traffordfc.com/",', '')
        evidence = reviewed_websites(ROOT)
        self.assertEqual(prove(ROOT, original, proposed, proposed, {'approved': []}, evidence), (0, 2))
        with self.assertRaisesRegex(ValueError, 'replacement or removal'):
            prove(ROOT, original, proposed, original, {'approved': []}, evidence)
        with self.assertRaisesRegex(ValueError, 'replacement or removal'):
            prove(ROOT, original, proposed.replace('"Other":"https://other.example/"', ''), proposed,
                  {'approved': []}, evidence)

    def test_website_plan_uses_exact_identity_and_current_approval(self):
        beta = {'Test FC': 'https://test.example/', 'Test Town FC': 'https://test-town.example/'}
        evidence = {'Test FC': ({'club': 'Test FC', 'status': 'verified_official_club_site',
                                 'url': beta['Test FC']}, 'test-ledger.json')}
        additions, held = website_plan({}, beta, evidence)
        self.assertEqual([item['club'] for item, _ in additions], ['Test FC'])
        self.assertEqual([item['identity'] for item in held], ['Test Town FC'])
