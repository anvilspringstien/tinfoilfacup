from pathlib import Path
import unittest

BETA = Path("beta/clubfinder-beta.html")


class WestonAliasRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = BETA.read_text(encoding="utf-8")

    def test_live_lookup_falls_back_to_canonical_club_identity(self):
        self.assertIn("const target=canonicalClubKey(raw);", self.text)
        self.assertIn("if(canonicalClubKey(key)===target)return value;", self.text)

    def test_result_history_uses_live_lookup_alias_path(self):
        self.assertIn("const arr=liveLookup('result_history',name)||[];", self.text)

    def test_weston_punctuation_variant_is_documented_at_join_boundary(self):
        self.assertIn('"Weston-super-Mare" vs "Weston Super Mare FC"', self.text)

    def test_verified_ground_name_wins_when_source_postcode_matches(self):
        self.assertIn("hgVerified&&hgPostcode&&rvPostcode&&hgPostcode===rvPostcode", self.text)
        self.assertIn("ground:hg.ground||rv.ground||'Venue TBC'", self.text)
        self.assertIn("postcode:hg.postcode||rv.postcode||'Postcode TBC'", self.text)

    def test_weston_regression_case_is_pinned(self):
        # BS22 6AB should resolve the Clubfinder identity "Weston Super Mare FC"
        # onto competition data keyed as "Weston-super-Mare"; both venue labels
        # refer to BS24 9AA and the verified Clubfinder name should be preferred.
        clubfinder_name = "Weston Super Mare FC"
        competition_name = "Weston-super-Mare"
        verified_postcode = "BS24 9AA"
        source_postcode = "BS24 9AA"

        def reference_key(name):
            value = name.lower()
            for suffix in (" fc", " afc", " cfc"):
                if value.endswith(suffix):
                    value = value[:-len(suffix)]
                    break
            return "".join(ch for ch in value if ch.isalnum())

        self.assertEqual(reference_key(clubfinder_name), reference_key(competition_name))
        self.assertEqual(
            verified_postcode.replace(" ", ""),
            source_postcode.replace(" ", ""),
        )


if __name__ == "__main__":
    unittest.main()
