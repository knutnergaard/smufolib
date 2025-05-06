import unittest
from unittest.mock import Mock

from fontParts.fontshell import RFont, RGlyph

from smufolib.objects.font import Font
from tests.testUtils import SavedFontMixin


class TestFont(SavedFontMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.font, _ = self.objectGenerator("font")  # pylint: disable=E1101
        self.fontPath = self.saveFontToTemp()

    def test_initialization_with_None(self):
        result = Font()
        self.assertEqual(type(result), Font)

    def test_initialization_with_path(self):
        result = Font(self.fontPath)
        self.assertEqual(type(result), Font)

    def test_initialization_with_font(self):
        rFont = RFont(self.fontPath)
        result = Font(rFont)
        self.assertEqual(type(result), Font)

    def test_initialization_with_invalid_font(self):
        mock_invalidFont = Mock(spec=RFont)
        del mock_invalidFont.naked
        with self.assertRaises(TypeError):
            Font(mock_invalidFont)
