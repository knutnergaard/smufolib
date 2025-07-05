import copy
import unittest
import smufolib
from smufolib.objects.range import RANGES_LIB_KEY
from tests.testUtils import generateGlyph


class TestRange(unittest.TestCase):
    def setUp(self):
        # Using objectGenerator to create actual objects
        # pylint: disable=E1101
        self.font, _ = self.objectGenerator("font")
        self.smufl, _ = self.objectGenerator("smufl")
        self.otherSmufl, _ = self.objectGenerator("smufl")
        self.layer, _ = self.objectGenerator("layer")
        self.glyph, _ = self.objectGenerator("glyph")
        self.emptyRange, _ = self.objectGenerator("range")

        # pylint: enable=E1101
        # Create layer and assign to font
        self.layer = self.font.newLayer("testLayer")
        self.font.defaultLayer = self.layer
        self.glyph1 = generateGlyph(
            self.font, "uniE080", unicode=0xE080, smuflName="timeSig0"
        )
        self.glyph2 = generateGlyph(
            self.font, "uniE081", unicode=0xE081, smuflName="timeSig1"
        )
        self.smufl.glyph = self.glyph1
        self._originalMetadata = smufolib.objects.range.METADATA
        smufolib.objects.range.METADATA = {
            "timeSignatures": {
                "description": "Time signatures",
                "glyphs": ["timeSig0", "timeSig1"],
                "range_start": "U+E080",
                "range_end": "U+E09F",
            },
            "staffBracketsAndDividers": {
                "description": "Staff brackets and dividers",
                "glyphs": ["brace", "bracket"],
                "range_end": "U+E00F",
                "range_start": "U+E000",
            },
        }
        self.addCleanup(self._restoreMetadata)
        self.range = self.glyph1.smufl.ranges[0]

    def _restoreMetadata(self):
        smufolib.objects.range.METADATA = self._originalMetadata

    def test_repr(self):
        expected_repr = (
            f"<{self.range.__class__.__name__} {self.range.name!r} "
            f"({self.range.strStart}-{self.range.strEnd}) editable=False at {id(self.range)}>"
        )
        self.assertEqual(repr(self.range), expected_repr)

    def test_eq_hash(self):
        range1 = self.range
        range2 = copy.copy(range1)
        self.assertEqual(range1, range2)
        self.assertEqual(hash(range1), hash(range2))

    # -----------------
    # Glyph Interaction
    # -----------------

    def test_contains(self):
        self.assertTrue("timeSig0" in self.range)
        self.assertFalse("uniE080" in self.range)

    def test_getitem_basic(self):
        result = self.range["timeSig0"]
        self.assertEqual(result, self.glyph1)

    def test_getitem_no_smufl(self):
        with self.assertRaises(KeyError):
            self.assertIsNone(self.emptyRange["timeSig0"])

    def test_getitem_no_unicode(self):
        self.glyph1.unicode = None
        with self.assertRaises(KeyError):
            result = self.range["timeSig0"]
            self.assertEqual(result, self.glyph1)

    def test_setitem_basic(self):
        self.range["timeSig2"] = self.glyph
        glyph = self.range["timeSig2"]
        self.assertEqual(glyph.name, "uniE082")
        self.assertEqual(glyph.unicode, 0xE082)

    def test_setitem_no_font(self):
        self.emptyRange["brace"] = self.glyph
        self.assertFalse("brace" in self.emptyRange)

    def test_setitem_unicode_out_of_range(self):
        with self.assertRaises(ValueError):
            self.range["brace"] = self.glyph
            print("brace" in self.range.smufl)
            self.assertNotIn("brace", self.range)

    def test_delitem_basic(self):
        del self.range["timeSig0"]
        self.assertFalse("timeSig0" in self.range)

    def test_delitem_no_font(self):
        del self.emptyRange["timeSig0"]
        self.assertTrue("timeSig0" in self.range)

    def test_iter(self):
        self.assertEqual(list(self.range), list(self.range.glyphs))

    def test_keys(self):
        self.assertEqual(list(self.range.keys()), ["timeSig0", "timeSig1"])

    # -------
    # Parents
    # -------

    def test_smufl(self):
        self.range.smufl = None
        self.range.smufl = self.smufl
        self.assertEqual(self.range.smufl, self.smufl)
        self.range.smufl = self.otherSmufl
        self.assertEqual(self.range.smufl, self.otherSmufl)

    def test_glyph(self):
        self.assertEqual(self.range.glyph, self.glyph1)
        self.range._smufl = None  # pylint: disable=W0212
        self.assertIsNone(self.range.glyph)

    def test_font(self):
        self.assertEqual(self.range.font, self.font)
        self.range._smufl = None  # pylint: disable=W0212
        self.assertIsNone(self.range.font)

    def test_layer(self):
        self.assertEqual(self.range.layer, self.layer)
        self.range._smufl = None  # pylint: disable=W0212
        self.assertIsNone(self.range.layer)

    def test_name(self):
        self.assertEqual(self.range.name, "timeSignatures")
        del smufolib.objects.range.METADATA["timeSignatures"]
        self.assertIsNone(self.range.name)

    def test_description(self):
        self.assertEqual(self.range.description, "Time signatures")
        smufolib.objects.range.METADATA["timeSignatures"]["description"] = 1.0
        self.assertIsNone(self.range.description)

    def test_strStart(self):
        self.assertEqual(self.range.strStart, "U+E080")
        smufolib.objects.range.METADATA["timeSignatures"]["range_start"] = 1.0
        self.assertIsNone(self.range.strStart)

    def test_strEnd(self):
        self.assertEqual(self.range.strEnd, "U+E09F")
        smufolib.objects.range.METADATA["timeSignatures"]["range_end"] = 1.0
        self.assertIsNone(self.range.strEnd)

    def test_start(self):
        self.assertEqual(self.range.start, 0xE080)
        smufolib.objects.range.METADATA["timeSignatures"]["range_start"] = 1.0
        self.assertIsNone(self.range.start)

    def test_end(self):
        self.assertEqual(self.range.end, 0xE09F)
        smufolib.objects.range.METADATA["timeSignatures"]["range_end"] = 1.0
        self.assertIsNone(self.range.end)

    def test_glyphs(self):
        self.assertEqual(self.range.glyphs, (self.glyph1, self.glyph2))
        smufolib.objects.range.METADATA["timeSignatures"]["range_start"] = "U+E080"
        smufolib.objects.range.METADATA["timeSignatures"]["glyphs"] = []
        self.assertIsNone(self.range.glyphs)

    def test_getAttribute_without_metadata(self):
        smufolib.objects.range.METADATA = None
        self.assertIsNone(self.range.end)

    def test_internal_metadata(self):
        smufolib.objects.range.METADATA["timeSignatures"]["range_start"] = 0xE080
        smufolib.objects.range.METADATA["timeSignatures"]["range_end"] = 0xE09F
        self.font.lib[RANGES_LIB_KEY] = smufolib.objects.range.METADATA
        self.assertEqual(self.range.strStart, "U+E080")
        self.assertEqual(self.range.strEnd, "U+E09F")
