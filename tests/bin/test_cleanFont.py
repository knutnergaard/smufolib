import sys
import unittest
from unittest.mock import MagicMock, patch

from smufolib.objects.smufl import ANCHOR_NAMES, FONT_ATTRIBUTES, GLYPH_ATTRIBUTES
from tests.testUtils import SavedFontMixin, SuppressOutputMixin, getVerboseOutput
from bin.cleanFont import cleanFont, main, _normalizeFont, _buildItemsDict, _parseArgs


class TestCleanFont(SavedFontMixin, SuppressOutputMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.font, _ = self.objectGenerator("font")  # pylint: disable=E1101
        self.font.smufl.name = "testFont"
        self.font.smufl.version = 1.0
        self.font.info.unitsPerEm = 1000
        self.font.smufl.designSize = 10
        self.font.smufl.sizeRange = (10, 20)
        self.font.smufl.engravingDefaults.stemThickness = 1.5
        self.font.smufl.spaces = True

        self.glyph = self.font.newGlyph("testGlyph")
        self.glyph.smufl.name = "smuflName"
        self.glyph.smufl.description = "testGlyph description"
        self.glyph.smufl.classes = ["class1", "class2"]
        self.smuflAnchor1 = self.glyph.appendAnchor("splitStemUpSE", (1, 2))
        self.smuflAnchor2 = self.glyph.appendAnchor("cutOutNW", (1, 2))
        self.nonSmuflAnchor = self.glyph.appendAnchor("nonSmuflAnchor", (3, 4))

        self.saveFontToTemp()
        self.suppressOutput()

    def verifyCleanup(self, exclude=None):
        for attr in FONT_ATTRIBUTES:
            result = getattr(self.font.smufl, attr)
            if attr == "engravingDefaults":
                result = getattr(self.font.smufl.engravingDefaults, "stemThickness")
            if exclude and attr in exclude:
                self.assertTrue(result)
            else:
                self.assertFalse(result)

        for attr in GLYPH_ATTRIBUTES:
            result = getattr(self.glyph.smufl, attr)
            if exclude and attr in exclude:
                self.assertTrue(result)
            else:
                self.assertFalse(result)

        anchorNames = [a.name for a in self.glyph.anchors]
        for name in ANCHOR_NAMES:
            if exclude and name in exclude:
                self.assertIn(name, anchorNames)
            else:
                self.assertNotIn(name, anchorNames)
        self.assertIn(self.nonSmuflAnchor.name, anchorNames)

    def test_cleanFont_removes_all(self):
        cleanFont(self.font, include="*")
        self.verifyCleanup()

    def test_cleanFont_removes_exclude_anchor(self):
        cleanFont(self.font, include="*", exclude=["splitStemUpSE"])
        self.verifyCleanup(exclude=["splitStemUpSE"])

    def test_cleanFont_falsy_attribute(self):
        self.glyph.smufl.name = None
        cleanFont(self.font, include=["name"])
        self.assertIsNone(self.glyph.smufl.name)

    def test_cleanFont_invalid_attribute(self):
        with self.assertRaises(ValueError):
            cleanFont(self.font, include="invalidAttribute")

    def test_cleanFont_verbose(self):
        output = getVerboseOutput(cleanFont, self.font, include="*", verbose=True)
        self.assertIn("\nCleaning attributes for font:", output)
        self.assertIn(f"\nCleaning attributes from glyph '{self.glyph.name}':", output)
        self.assertIn(f"\nCleaning anchors from glyph '{self.glyph.name}':", output)
        self.assertIn(f"\t'{self.smuflAnchor1.name}'", output)
        self.assertIn("Saving font...", output)

    @patch("bin.cleanFont.Font.save")
    def test_calculateEngravingDefaults_calls_save(self, mock_save):
        cleanFont(self.font, include="*")
        mock_save.assert_called_once()

    @patch("bin.cleanFont.cleanFont")
    def test_main(self, mock_cleanFont):
        include = "*"
        exclude = ["name", "description", "classes"]
        test_args = [
            "cleanFont",
            str(self.fontPath),
            include,
            "--exclude",
            *exclude,
            "--verbose",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        mock_cleanFont.assert_called_once()
        args, kwargs = mock_cleanFont.call_args
        self.assertIsInstance(args[0], type(self.font))
        self.assertEqual(args[1], [include])
        self.assertEqual(kwargs["exclude"], exclude)
        self.assertTrue(kwargs["verbose"])

    def test_normalizeFont_accepts_path(self):
        result = _normalizeFont(self.fontPath)
        self.assertIsInstance(result, type(self.font))
