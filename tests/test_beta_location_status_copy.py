"""The three public location indicators must distinguish recorded and verified grounds."""

from pathlib import Path
import unittest

HTML = (Path(__file__).resolve().parents[1] / "beta/clubfinder-beta.html").read_text(encoding="utf-8")

RECORDED = "Ground details recorded. Verification pending."
OLD_WARNING = "⚠️ Unverified Location - Please check before travelling."


class LocationStatusCopyTests(unittest.TestCase):
    def test_all_three_paths_use_the_same_recorded_but_pending_copy(self):
        self.assertEqual(HTML.count(RECORDED), 3)
        self.assertNotIn(OLD_WARNING, HTML)

    def test_fixture_venue_keeps_three_distinct_states(self):
        self.assertIn("if(hasCoords&&verified)return {text:'✅ Verified Location.',colour:'#176b2c'};", HTML)
        self.assertIn("if(hasLocation)return {text:'" + RECORDED + "',colour:'#486673'};", HTML)
        self.assertIn("return {text:'❌ No location data available.',colour:'#a32626'};", HTML)

    def test_origin_and_custodian_keep_verified_and_missing_states(self):
        self.assertIn("const loc=verified?'✅ Verified Location.':hasLoc?'" + RECORDED + "':'❌ No location data available.'", HTML)
        self.assertIn("const currentLoc=currentVerified?'✅ Verified Location.':currentHasLoc?'" + RECORDED + "':'❌ No location data available.'", HTML)
        self.assertIn("lc=verified?'#176b2c':hasLoc?'#486673':'#a32626'", HTML)
        self.assertIn("currentLc=currentVerified?'#176b2c':currentHasLoc?'#486673':'#a32626'", HTML)


if __name__ == "__main__":
    unittest.main()
