import sys
import unittest
from unittest.mock import patch, MagicMock

from tests.testUtils import SavedFontMixin, SavedMetadataMixin, SuppressOutputMixin
from bin.checkAnchors import (
    checkAnchors,
    main,
    _normalizeFont,
    _normalizeColor,
    _normalizeJsonDict,
    _normalizeRequest,
    _evaluate,
)


class TestCheckAnchors(
    SavedFontMixin, SavedMetadataMixin, SuppressOutputMixin, unittest.TestCase
):
    def setUp(self):
        super().setUp()
        self.font, _ = self.objectGenerator("font")  # pylint: disable=E1101
        self.font.info.familyName = "testFont"
        self.font.info.styleName = "Regular"
        self.glyph = self.font.newGlyph("glyph")

        self.glyph.smufl.name = "noteheadBlack"
        self.glyph.name = "noteheadBlack"
        self.glyph.appendAnchor("anchor1", (10, 10))
        self.glyph.appendAnchor("anchor2", (10, 10))

        for i, a in enumerate(self.glyph.anchors):
            a.name = f"anchor{i + 1}"

        self.metadata = {
            "glyphsWithAnchors": {"noteheadBlack": {"anchor1": {}, "anchor3": {}}}
        }

        self.saveFontToTemp()
        self.saveMetadataToTemp()
        self.suppressOutput()

    @patch("bin.checkAnchors._normalizeJsonDict")
    @patch("bin.checkAnchors._normalizeRequest")
    def test_checkAnchors_discrepancies_logged(self, mock_request, mock_json):
        mock_request.return_value = MagicMock(json=lambda: self.metadata)
        mock_json.return_value = self.metadata

        with patch("builtins.print") as mock_print:
            checkAnchors(self.font, verbose=True)

        mock_print.assert_any_call("\nGlyphs with missing anchors:")
        mock_print.assert_any_call("\nGlyphs with superfluous anchors:")
        mock_print.assert_any_call("\nDone.")

    def test_checkAnchors_no_anchors(self):
        self.glyph.clearAnchors()
        with patch("builtins.print") as mock_print:
            checkAnchors(self.font, verbose=True)
        mock_print.assert_any_call("\nNo font anchors found.")

    def test_cherkAnchors_mark_glyphs(self):
        expectedColor = (1, 0, 0, 1)
        checkAnchors(self.font, mark=True, color=expectedColor)
        self.assertTupleEqual(self.glyph.markColor, expectedColor)

    @patch("bin.checkAnchors.checkAnchors")
    def test_main(self, mock_checkAnchors):
        test_color = ["1", "0", "0", "1"]

        test_args = [
            "checkAnchors",
            str(self.fontPath),
            "--font-data",
            str(self.metadataPath),
            "--mark",
            "--color",
            *test_color,
            "--verbose",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        mock_checkAnchors.assert_called_once()
        args, kwargs = mock_checkAnchors.call_args
        self.assertIsInstance(args[0], type(self.font))
        self.assertEqual(kwargs["fontData"].path, str(self.metadataPath))
        self.assertTrue(kwargs["mark"])
        self.assertListEqual(kwargs["color"], [int(i) for i in test_color])
        self.assertTrue(kwargs["verbose"])

    def test_normalizeFont_accepts_path(self):
        result = _normalizeFont(self.fontPath)
        self.assertIsInstance(result, type(self.font))

    def test_normalizeRequest_accepts_path(self):
        result = _normalizeRequest(self.metadataPath)
        self.assertEqual(result.path, str(self.metadataPath))

    def test_normalizeColor_raises_if_mark_and_color_None(self):
        with self.assertRaises(TypeError):
            _normalizeColor(None, mark=True)

    def test_normalizeJsonDict_raises_on_none(self):
        with self.assertRaises(TypeError):
            _normalizeJsonDict(None)

    def test_normalizeColor_mark_None(self):
        self.assertIsNone(_normalizeColor(color=None, mark=False))

    def test_evaluate_name_not_in_reference(self):
        test = {"noteheadWhite": {}}
        reference = self.metadata["glyphsWithAnchors"]
        self.assertListEqual(
            _evaluate(test=test, reference=reference, names={}, verbose=False), []
        )
