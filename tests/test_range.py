import unittest
import smufolib
import smufolib.objects


class TestRange(unittest.TestCase):
    def setUp(self):
        # Using objectGenerator to create actual objects
        # pylint: disable=E1101
        self.font, _ = self.objectGenerator("font")
        self.smufl, _ = self.objectGenerator("smufl")
        self.layer, _ = self.objectGenerator("layer")
        self.range, _ = self.objectGenerator("range")

        # pylint: enable=E1101
        # Create layer and assign to font
        self.layer = self.font.newLayer("testLayer")
        self.font.defaultLayer = self.layer
        self.range.smufl = self.smufl
        self.glyph1 = self.generateGlyph("uniE080", 0xE080, "timeSig0")
        self.glyph2 = self.generateGlyph("uniE081", 0xE081, "timeSig1")
        self.smufl.glyph = self.glyph1

        smufolib.objects.range.METADATA = {
            "timeSignatures": {
                "description": "Time signatures",
                "glyphs": ["timeSig0", "timeSig1"],
                "range_start": "U+E080",
                "range_end": "U+E09F",
            }
        }

    def generateGlyph(self, name, unicode, smufl_name):
        glyph = self.font.newGlyph(name)
        glyph.unicode = unicode
        glyph.smufl.name = smufl_name
        return glyph

    def test_repr(self):
        expected_repr = (
            f"<{self.range.__class__.__name__} '{self.range.name}' "
            f"('{self.range.start}-{self.range.end}') at {id(self.range)}>"
        )
        self.assertEqual(repr(self.range), expected_repr)

    def test_smufl(self):
        self.assertEqual(self.range.smufl, self.smufl)

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
        smufolib.objects.range.METADATA[1] = smufolib.objects.range.METADATA[
            "timeSignatures"
        ]
        del smufolib.objects.range.METADATA["timeSignatures"]
        self.assertIsNone(self.range.name)

    def test_description(self):
        self.assertEqual(self.range.description, "Time signatures")
        smufolib.objects.range.METADATA["timeSignatures"]["description"] = 1
        self.assertIsNone(self.range.description)

    def test_start(self):
        self.assertEqual(self.range.start, "U+E080")
        smufolib.objects.range.METADATA["timeSignatures"]["range_start"] = 1
        self.assertIsNone(self.range.start)

    def test_end(self):
        self.assertEqual(self.range.end, "U+E09F")
        smufolib.objects.range.METADATA["timeSignatures"]["range_end"] = 1
        self.assertIsNone(self.range.end)

    def test_glyphs(self):
        self.assertEqual(self.range.glyphs, (self.glyph1, self.glyph2))
        smufolib.objects.range.METADATA["timeSignatures"]["range_start"] = "U+E080"
        smufolib.objects.range.METADATA["timeSignatures"]["glyphs"] = ()
        self.assertEqual(self.range.glyphs, ())

    def test_getAttribute_without_metadata(self):
        smufolib.objects.range.METADATA = None
        self.assertIsNone(self.range.end)
