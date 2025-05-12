import unittest

from smufolib.objects.engravingDefaults import (
    ENGRAVING_DEFAULTS_ATTRIBUTES,
)
from tests.testUtils import generateGlyph


class TestEngravingDefaults(unittest.TestCase):
    def setUp(self):
        # Create generic objects
        # pylint: disable=E1101
        self.font, _ = self.objectGenerator("font")
        self.other_font, _ = self.objectGenerator("font")
        self.smufl, _ = self.objectGenerator("smufl")
        self.other_smufl, _ = self.objectGenerator("smufl")
        self.engravingDefaults, _ = self.objectGenerator("engravingDefaults")
        self.otherEngravingDefaults, _ = self.objectGenerator("engravingDefaults")

        # Assign font to engravingDefaults
        self.smufl.font = self.font
        self.font.info.familyName = "testFont"
        self.engravingDefaults.smufl = self.smufl

        # Assign glyph to font
        self.font.newGlyph("testGlyph")
        self.glyph = self.font["testGlyph"]

        # Define libDict key
        self.libDictKey = "com.smufolib.engravingDefaults"

        # Define default update dict
        self.defaultDict = {"stemThickness": 1.0, "beamThickness": 2.0}

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

    def test_reprContents_no_font(self):
        self.assertListEqual(self.otherEngravingDefaults._reprContents(), [])

    # -------
    # Parents
    # -------

    def test_get_smufl(self):
        self.assertIs(self.engravingDefaults.smufl, self.smufl)
        self.assertIsNone(self.otherEngravingDefaults.smufl)

    def test_set_smufl_with_preset_smufl(self):
        with self.assertRaises(AssertionError):
            self.engravingDefaults.smufl = self.other_smufl

    def test_get_font(self):
        self.assertIs(self.engravingDefaults.font, self.font)
        self.assertIsNone(self.otherEngravingDefaults.font)

    def test_get_glyph(self):
        self.assertIs(self.glyph.smufl.engravingDefaults.glyph, self.glyph)
        self.assertIsNone(self.otherEngravingDefaults.glyph)

    def test_get_layer(self):
        self.assertIs(self.glyph.smufl.engravingDefaults.layer, self.glyph.layer)
        self.assertIsNone(self.otherEngravingDefaults.layer)

    # ----
    # Auto
    # ----

    def test_auto(self):
        self.engravingDefaults.auto = False
        self.assertFalse(self.engravingDefaults.auto)
        self.engravingDefaults.auto = True
        self.assertTrue(self.engravingDefaults.auto)

    # ----------
    # Attributes
    # ----------

    def _test_attribute_assignment(self, spaces):
        testFonts = ("font1", "font2")
        if spaces:
            self._set_spaces()
        result = {}
        for attr in ENGRAVING_DEFAULTS_ATTRIBUTES:
            with self.subTest(attr=attr):
                numeric_value = 1.0 if spaces else 250
                value = testFonts if attr == "textFontFamily" else numeric_value
                result[attr] = value
                setattr(self.engravingDefaults, attr, value)
                self.assertEqual(getattr(self.engravingDefaults, attr), value)
        self.maxDiff = None
        self.assertDictEqual(self.engravingDefaults.items(), result)

    def test_get_attributes_auto_true(self):
        ed = self.font.smufl.engravingDefaults
        ed.auto = True
        # Generate stem glyph
        generateGlyph(
            self.font,
            "uniE210",
            unicode=0xE210,
            points=((0, 0), (20, 0), (20, 250), (0, 250)),
        )
        self.assertEqual(ed.stemThickness, 20)

    def test_get_attributes_auto_false(self):
        ed = self.font.smufl.engravingDefaults
        ed.auto = False
        # Generate stem glyph
        generateGlyph(
            self.font,
            "uniE210",
            unicode=0xE210,
            points=((0, 0), (20, 0), (20, 250), (0, 250)),
        )
        self.assertIsNone(ed.stemThickness)

    def test_set_attributes_basic(self):
        self._test_attribute_assignment(False)
        self._test_attribute_assignment(True)

    def test_set_attributes_None(self):
        self.font.lib[self.libDictKey] = self.defaultDict
        self.engravingDefaults.stemThickness = None
        self.assertNotIn("stemThickness", self.font.lib[self.libDictKey])
        self.engravingDefaults.beamThickness = None
        self.assertNotIn(self.libDictKey, self.font.lib)

    def test_set_attribute_no_font(self):
        self.otherEngravingDefaults.stemThickness = 1.0
        self.assertIsNone(self.otherEngravingDefaults.stemThickness)

    def test_set_attribute_no_value(self):
        self.engravingDefaults.stemThickness = 0
        self.assertIsNone(self.engravingDefaults.stemThickness)

    def test_clear(self):
        self.font.lib[self.libDictKey] = self.defaultDict
        self.engravingDefaults.clear()
        self.assertIsNone(self.engravingDefaults.stemThickness)

    def test_clear_no_font(self):
        self.assertIsNone(self.otherEngravingDefaults.clear())

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

    def test_update_basic(self):
        self.assertIsNone(self.engravingDefaults.update(None))
        self.engravingDefaults.update(self.defaultDict)
        self.assertEqual(self.engravingDefaults.stemThickness, 1.0)
        self.assertEqual(self.engravingDefaults.beamThickness, 2.0)

    def test_update_kwargs(self):
        self.engravingDefaults.update(**self.defaultDict)
        self.assertEqual(self.engravingDefaults.stemThickness, 1.0)
        self.assertEqual(self.engravingDefaults.beamThickness, 2.0)

    def test_update_preexisting_libDict(self):
        self.font.lib[self.libDictKey] = {"stemThickness": 2.0}
        self.engravingDefaults.update(self.defaultDict)
        self.assertEqual(self.engravingDefaults.stemThickness, 1.0)
        self.assertEqual(self.engravingDefaults.beamThickness, 2.0)

    def test_update_with_spaces(self):
        self.font.info.unitsPerEm = 1000
        self.engravingDefaults.spaces = True
        self.engravingDefaults.update(self.defaultDict)
        self.assertEqual(self.font.lib[self.libDictKey]["stemThickness"], 250)
        self.assertEqual(self.font.lib[self.libDictKey]["beamThickness"], 500)

    def test_update_invalid_attribute(self):
        updateDict = {"invalidAttribute": 1.0, "beamThickness": 2.0}
        with self.assertRaises(AttributeError):
            self.engravingDefaults.update(updateDict)

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
        self.otherEngravingDefaults.spaces = None
        self.otherEngravingDefaults.spaces = True
        self.assertFalse(self.otherEngravingDefaults.spaces)

    def test_libDict_no_font(self):
        self.otherEngravingDefaults._libDict = {"testAttribute": 0}
        self.assertDictEqual(self.engravingDefaults._libDict, {})
