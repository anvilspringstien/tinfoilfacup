from pathlib import Path
import re
import unittest

HTML = Path('clubfinder.html')


class PigeonMilesStatsPatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = HTML.read_text(encoding='utf-8')

    def test_patch_markers_present_once(self):
        self.assertEqual(self.text.count('/* TIN_FOIL_PIGEON_MILES_STATS_BEGIN */'), 1)
        self.assertEqual(self.text.count('/* TIN_FOIL_PIGEON_MILES_STATS_END */'), 1)

    def test_stats_uses_saved_campaign_start_postcode(self):
        self.assertIn('savedJourneyForStats&&savedJourneyForStats.postcode', self.text)

    def test_round_trip_formula_is_two_times_haversine(self):
        self.assertIn('sum+(2*hav(start,venue))', self.text)

    def test_each_played_crumb_uses_canonical_stats_venue(self):
        self.assertIn("const v=venueForResult(((cr||{}).result)||{});", self.text)

    def test_walkovers_do_not_add_travel(self):
        self.assertIn(".decision||'').toLowerCase()!=='walkover'", self.text)

    def test_unresolved_locations_fail_closed(self):
        self.assertGreaterEqual(self.text.count("display:'Awaiting venue location'"), 2)

    def test_display_rounds_only_at_end(self):
        self.assertIn('display:String(Math.round(miles))', self.text)
        helper = self.text.split('/* TIN_FOIL_PIGEON_MILES_STATS_BEGIN */',1)[1].split('/* TIN_FOIL_PIGEON_MILES_STATS_END */',1)[0]
        self.assertNotRegex(helper, r'Math\.round\([^)]*hav\(')

    def test_stats_certificate_labels_pigeon_miles(self):
        self.assertIn('• Pigeon Miles Travelled:', self.text)
        self.assertIn('Pigeon Miles = twice the straight-line distance from your Campaign start postcode to each tie venue.', self.text)
        self.assertNotIn('Travel mileage is deliberately not counted yet.', self.text)

    def test_popup_opens_once_and_before_first_await_in_certificate(self):
        self.assertEqual(self.text.count('const w=window.open("","_blank");'), 1)
        start = self.text.index('async function journeyCertificate(origin)')
        sample = self.text[start:start+1800]
        popup = sample.index('const w=window.open("","_blank");')
        first_await = sample.index('await tinFoilPigeonMilesForStats')
        self.assertLess(popup, first_await)

    def test_pigeon_geocoder_does_not_call_mutating_lookup(self):
        helper = self.text.split('/* TIN_FOIL_PIGEON_MILES_STATS_BEGIN */',1)[1].split('/* TIN_FOIL_PIGEON_MILES_STATS_END */',1)[0]
        self.assertNotIn('lookup(', helper)
        self.assertIn('fetch(PCAPI+encodeURIComponent(pc))', helper)


if __name__ == '__main__':
    unittest.main()
