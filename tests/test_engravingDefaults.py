import unittest
from smufolib.objects.engravingDefaults import ENGRAVING_DEFAULTS_KEYS


class TestEngravingDefaults(unittest.TestCase):
    def setUp(self):
        # Create generic objects
        # pylint: disable=E1101
        self.font, _ = self.objectGenerator("font")
        self.other_font, _ = self.objectGenerator("font")
        self.smufl, _ = self.objectGenerator("smufl")
        self.other_smufl, _ = self.objectGenerator("smufl")
        self.engravingDefaults, _ = self.objectGenerator("engravingDefaults")
        self.other_engravingDefaults, _ = self.objectGenerator("engravingDefaults")

        # Assign font to engravingDefaults
        self.smufl.font = self.font
        self.font.info.familyName = "testFont"
        self.engravingDefaults.smufl = self.smufl

        # Assign glyph to font
        self.font.newGlyph("testGlyph")
        self.glyph = self.font["testGlyph"]

    def _set_spaces(self):
        self.engravingDefaults.font.info.unitsPerEm = 1000
        self.engravingDefaults.spaces = True

    # ----
    # init
    # ----

    def test_initialization(self):
        self.assertIsInstance(self.engravingDefaults, type(self.engravingDefaults))
        self.assertIs(self.engravingDefaults.smufl, self.smufl)
        self.assertIs(self.engravingDefaults.font, self.font)

    # ----
    # repr
    # ----

    # pylint: disable=W0212
    def test_reprContents(self):
        value = self.engravingDefaults._reprContents()
        self.assertIn("in font", value)
        self.assertIsInstance(value, list)
        for i in value:
            self.assertIsInstance(i, str)

    # -------
    # Parents
    # -------

    def test_get_smufl(self):
        self.assertIs(self.engravingDefaults.smufl, self.smufl)
        self.assertIsNone(self.other_engravingDefaults.smufl)

    def test_set_smufl_with_preset_smufl(self):
        with self.assertRaises(AssertionError):
            self.engravingDefaults.smufl = self.other_smufl

    def test_get_font(self):
        self.assertIs(self.engravingDefaults.font, self.font)
        self.assertIsNone(self.other_engravingDefaults.font)

    def test_get_glyph(self):
        self.assertIs(self.glyph.smufl.engravingDefaults.glyph, self.glyph)
        self.assertIsNone(self.other_engravingDefaults.glyph)

    def test_get_layer(self):
        self.assertIs(self.glyph.smufl.engravingDefaults.layer, self.glyph.layer)
        self.assertIsNone(self.other_engravingDefaults.layer)

    # ----------
    # Attributes
    # ----------

    def _set_and_assert_attribute(self, attr, value):
        setattr(self.engravingDefaults, attr, value)
        self.assertEqual(getattr(self.engravingDefaults, attr), value)

    def _test_attribute_assignment(self, spaces):
        testFonts = ("font1", "font2")
        if spaces:
            self._set_spaces()
        for attr in ENGRAVING_DEFAULTS_KEYS:
            with self.subTest(attr=attr):
                numeric_value = 1.0 if spaces else 250
                value = testFonts if attr == "textFontFamily" else numeric_value
                self._set_and_assert_attribute(attr, value)

    def test_attributes(self):
        self._test_attribute_assignment(False)
        self._test_attribute_assignment(True)

    def test_set_attribute_no_font(self):
        self.other_engravingDefaults.stemThickness = 1.0
        self.assertIsNone(self.other_engravingDefaults.stemThickness)

    def test_set_attribute_no_value(self):
        self.engravingDefaults.stemThickness = 0
        self.assertIsNone(self.engravingDefaults.stemThickness)

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
        self.assertIsNone(self.engravingDefaults.update(None))
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

    def test_update_with_invalid_attribute(self):
        update_dict = {"invalidAttribute": 1.0, "beamThickness": 2.0}
        with self.assertRaises(AttributeError):
            self.engravingDefaults.update(update_dict)

    def test_values(self):
        self.engravingDefaults.stemThickness = 1.0
        values = self.engravingDefaults.values()
        self.assertIsInstance(values, list)
        self.assertIn(1.0, values)

    def test_round(self):
        self.engravingDefaults.stemThickness = 1.5
        self.engravingDefaults.round()
        self.assertEqual(self.engravingDefaults.stemThickness, 2.0)

    def test_round_with_spaces(self):
        self._set_spaces()
        self.engravingDefaults.stemThickness = 1.5
        self.engravingDefaults.round()
        self.assertEqual(self.engravingDefaults.stemThickness, 1.5)

    def test_spaces(self):
        self.font.info.unitsPerEm = 1000
        self.assertFalse(self.engravingDefaults.spaces)
        self.smufl.spaces = True
        self.assertTrue(self.smufl.spaces)

    def test_spaces_no_font(self):
        self.other_engravingDefaults.spaces = None
        self.other_engravingDefaults.spaces = True
        self.assertFalse(self.other_engravingDefaults.spaces)
