import unittest


class TestGlyph(unittest.TestCase):
    def setUp(self):
        self.font, _ = self.objectGenerator("font")  # pylint: disable=E1101
        self.glyph = self.font.newGlyph("glyphName")  # pylint: disable=E1101
        self.libKey = "com.smufolib.names"
        self.defaultDict = {"smuflName": "glyphName"}

    def test_set_name_existing(self):
        self.font.lib[self.libKey] = self.defaultDict
        self.glyph.smufl.name = "smuflName"
        self.glyph.name = "newGlyphName"

        self.assertEqual(self.glyph.name, "newGlyphName")
        self.assertEqual(self.font.lib[self.libKey]["smuflName"], "newGlyphName")

    def test_set_name_not_existing(self):
        self.font.lib[self.libKey] = self.defaultDict
        self.glyph.name = "nonExistentName"
        self.assertNotIn(self.glyph.name, self.font.lib[self.libKey].values())
