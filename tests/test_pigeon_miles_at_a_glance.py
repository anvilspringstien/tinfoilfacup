from pathlib import Path
import unittest

HTML=Path('clubfinder.html')

class PigeonMilesGlanceRegression(unittest.TestCase):
    def test_glance_card_and_existing_logic(self):
        text=HTML.read_text(encoding='utf-8')
        self.assertEqual(text.count('TIN_FOIL_PIGEON_MILES_GLANCE'),1)
        self.assertIn('Pigeon<br>Miles',text)
        self.assertIn('🐦',text)
        self.assertIn("certEsc(pigeonMilesDisplay)",text)
        self.assertIn('Pigeon Miles Travelled:',text)
        self.assertIn('2*hav(start,venue)',text)
        self.assertIn('Pigeon Miles = twice the straight-line distance from your Campaign start postcode to each tie venue.',text)
        self.assertNotIn('500 Pigeon',text)
        self.assertNotIn('1,000 Pigeon',text)

if __name__=='__main__': unittest.main()
