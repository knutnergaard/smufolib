import unittest


class TestGlyph(unittest.TestCase):
    def setUp(self):
        self.font, _ = self.objectGenerator("font")  # pylint: disable=E1101
        self.glyph = self.font.newGlyph("glyphName")  # pylint: disable=E1101

    def test_set_name_with_existing_name(self):
        """Should update the `namesDict` if name is found in values."""
        self.font.lib["com.smufolib.names"] = {"smuflName": "glyphName"}
        self.glyph.smufl.name = "smuflName"
        self.glyph.name = "newGlyphName"

        self.assertEqual(self.glyph.name, "newGlyphName")
        self.assertEqual(
            self.font.lib["com.smufolib.names"]["smuflName"], "newGlyphName"
        )
