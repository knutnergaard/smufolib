import unittest

from smufolib.utils.scriptUtils import (
    normalizeFont,
    normalizeRequest,
    normalizeColor,
    normalizeJsonDict,
    normalizeTargetPath,
)
from tests.testUtils import SavedFontMixin, SavedMetadataMixin


class TestSCriptUitls(SavedFontMixin, SavedMetadataMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.font, _ = self.objectGenerator("font")  # pylint: disable=E1101
        self.metadata = {
            "glyphsWithAnchors": {"noteheadBlack": {"anchor1": {}, "anchor3": {}}}
        }
        self.saveFontToTemp()
        self.saveMetadataToTemp()

    def test_normalizeFont_accepts_path(self):
        result = normalizeFont(self.fontPath)
        self.assertIsInstance(result, type(self.font))

    def test_normalizeRequest_accepts_path(self):
        result = normalizeRequest(self.metadataPath)
        self.assertEqual(result.path, str(self.metadataPath))

    def test_normalizeColor_raises_if_mark_and_color_None(self):
        with self.assertRaises(TypeError):
            normalizeColor(None, mark=True)

    def test_normalizeJsonDict_raises_on_none(self):
        with self.assertRaises(TypeError):
            normalizeJsonDict(None)

    def test_normalizeColor_mark_None(self):
        self.assertIsNone(normalizeColor(color=None, mark=False))

    def test_normalizeTargetPath(self):
        self.assertEqual(normalizeTargetPath(self.fontPath), self.fontPath)
        with self.assertRaises(FileNotFoundError):
            normalizeTargetPath("nonExistentPath")
