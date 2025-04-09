import json
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

from tests.testUtils import SuppressOutputMixin
from bin.checkAnchors import (
    checkAnchors,
    main,
    _normalizeFont,
    _normalizeColor,
    _normalizeJsonDict,
    _normalizeRequest,
    _evaluate,
)


class TestCheckAnchors(unittest.TestCase, SuppressOutputMixin):
    def setUp(self):
        # Define generic objects
        # pylint: disable=E1101
        self.font, _ = self.objectGenerator("font")
        self.font.info.familyName = "testFont"
        self.font.info.styleName = "Regular"
        self.glyph = self.font.newGlyph("glyph")
        # pylint: enable=E1101

        self.glyph.smufl.name = "noteheadBlack"
        self.glyph.name = "noteheadBlack"
        self.glyph.appendAnchor("anchor1", (10, 10))
        self.glyph.appendAnchor("anchor2", (10, 10))

        for i, a in enumerate(self.glyph.anchors):
            a.name = f"anchor{i + 1}"

        self.metadata = {
            "glyphsWithAnchors": {"noteheadBlack": {"anchor1": {}, "anchor3": {}}}
        }

        # Supress console output
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
        with tempfile.TemporaryDirectory() as tempDir:
            fontPath = Path(tempDir) / "testFont.ufo"
            self.font.save(str(fontPath))

            metadataPath = Path(tempDir) / "metadata.json"
            metadataPath.write_text(json.dumps(self.metadata))

            test_color = ["1", "0", "0", "1"]

            test_args = [
                "checkAnchors",
                str(fontPath),
                "--font-data",
                str(metadataPath),
                "--mark",
                "--color",
                *test_color,
                "--verbose",
            ]

            with patch.object(sys, "argv", test_args):
                main()

            mock_checkAnchors.assert_called_once()
            kwargs = mock_checkAnchors.call_args.kwargs

            self.assertIsInstance(kwargs["font"], type(self.font))
            self.assertEqual(kwargs["fontData"].path, str(metadataPath))
            self.assertTrue(kwargs["mark"])
            self.assertListEqual(kwargs["color"], [int(i) for i in test_color])
            self.assertTrue(kwargs["verbose"])

    def test_normalizeFont_accepts_path(self):
        with tempfile.TemporaryDirectory() as tempDir:
            fontPath = Path(tempDir) / "testFont.ufo"
            self.font.save(str(fontPath))
            result = _normalizeFont(fontPath)
            self.assertIsInstance(result, type(self.font))

    def test_normalizeRequest_accepts_path(self):
        with tempfile.TemporaryDirectory() as tempDir:
            metadataPath = Path(tempDir) / "metadata.json"
            metadataPath.write_text(json.dumps(self.metadata))
            result = _normalizeRequest(metadataPath)
            self.assertEqual(result.path, str(metadataPath))

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
