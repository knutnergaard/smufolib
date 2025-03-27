import unittest
from smufolib.objects.engravingDefaults import ENGRAVING_DEFAULTS_KEYS


class TestEngravingDefaults(unittest.TestCase):
    def setUp(self):
        # Create generic objects
        # pylint: disable=E1101
        self.font, _ = self.objectGenerator("font")
        self.smufl, _ = self.objectGenerator("smufl")
        self.engravingDefaults, _ = self.objectGenerator("engravingDefaults")

        # Assign font to engravingDefaults
        self.smufl.font = self.font
        self.font.info.familyName = "testFont"
        self.engravingDefaults.smufl = self.smufl

        # Assign glyph to font
        self.font.newGlyph("testGlyph")
        self.glyph = self.font["testGlyph"]

    def test_initialization(self):
        self.assertIsInstance(self.engravingDefaults, type(self.engravingDefaults))
        self.assertIs(self.engravingDefaults.smufl, self.smufl)

    def test_attributes(self):
        testFonts = ("font1", "font2")
        for attr in ENGRAVING_DEFAULTS_KEYS:
            with self.subTest(attr=attr):
                if attr == "textFontFamily":
                    setattr(self.engravingDefaults, attr, testFonts)
                    self.assertEqual(getattr(self.engravingDefaults, attr), testFonts)
                else:
                    setattr(self.engravingDefaults, attr, 1.0)
                    self.assertEqual(getattr(self.engravingDefaults, attr), 1.0)

    def test_set_attributes_no_font(self):
        # pylint: disable=E1101
        engravingDefaults = self.objectGenerator("engravingDefaults")
        with self.assertRaises(AttributeError):
            engravingDefaults.stemThickness = 1.0

    def test_clear(self):
        self.font.lib["com.smufolib.engravingDefaults"] = {"stemThickness": 1.0}
        self.engravingDefaults.clear()
        self.assertIsNone(self.engravingDefaults.stemThickness)

    def test_items(self):
        self.engravingDefaults.stemThickness = 1.0
        items = self.engravingDefaults.items()
        self.assertIsInstance(items, dict)
        self.assertIn("stemThickness", items)
        self.assertEqual(items["stemThickness"], 1.0)

    def test_keys(self):
        keys = self.engravingDefaults.keys()
        self.assertIsInstance(keys, list)
        self.assertIn("stemThickness", keys)

    def test_update(self):
        update_dict = {"stemThickness": 1.0, "beamThickness": 2.0}
        self.engravingDefaults.update(update_dict)
        self.assertEqual(self.engravingDefaults.stemThickness, 1.0)
        self.assertEqual(self.engravingDefaults.beamThickness, 2.0)

    def test_update_with_spaces(self):
        self.font.info.unitsPerEm = 1000
        self.engravingDefaults.spaces = True
        update_dict = {"stemThickness": 1.0, "beamThickness": 2.0}
        self.engravingDefaults.update(update_dict)
        self.assertEqual(
            self.font.lib["com.smufolib.engravingDefaults"]["stemThickness"], 250
        )
        self.assertEqual(
            self.font.lib["com.smufolib.engravingDefaults"]["beamThickness"], 500
        )

    def test_values(self):
        self.engravingDefaults.stemThickness = 1.0
        values = self.engravingDefaults.values()
        self.assertIsInstance(values, list)
        self.assertIn(1.0, values)

    def test_round(self):
        self.engravingDefaults.stemThickness = 1.5
        self.engravingDefaults.round()
        self.assertEqual(self.engravingDefaults.stemThickness, 2.0)

    def test_spaces(self):
        self.font.info.unitsPerEm = 1000
        self.assertFalse(self.engravingDefaults.spaces)
        self.smufl.spaces = True
        self.assertTrue(self.smufl.spaces)

    def test_smufl(self):
        self.assertIs(self.engravingDefaults.smufl, self.smufl)

    def test_font(self):
        self.assertIs(self.engravingDefaults.font, self.font)

    def test_glyph(self):
        self.assertIs(self.glyph.smufl.engravingDefaults.glyph, self.glyph)

    def test_layer(self):
        self.assertIs(self.glyph.smufl.engravingDefaults.layer, self.glyph.layer)
