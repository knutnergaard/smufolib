import sys
import unittest
from unittest.mock import patch, MagicMock

from tests.testUtils import SavedFontMixin, SavedMetadataMixin, SuppressOutputMixin
from bin.checkAnchors import (
    checkAnchors,
    main,
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
            "glyphsWithAnchors": {
                "noteheadBlack": {"anchor1": (), "anchor3": ()},
                "noteheadWhite": {"anchor2": ()},
            },
        }

        self.saveFontToTemp()
        self.saveMetadataToTemp()
        self.suppressOutput()

    @patch("smufolib.utils.scriptUtils.normalizeJsonDict")
    @patch("smufolib.utils.scriptUtils.normalizeRequest")
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

    def test_evaluate_name_not_in_reference(self):
        test = {"noteheadHalf": {}}
        reference = self.metadata["glyphsWithAnchors"]
        self.assertListEqual(
            _evaluate(test=test, reference=reference, names={}, verbose=False), []
        )

    def test_evaluate_ahchor_in_reference_name(self):
        test = {"noteheadWhite": {"anchor2": ()}}
        reference = self.metadata["glyphsWithAnchors"]
        self.assertListEqual(
            _evaluate(test=test, reference=reference, names={}, verbose=False), []
        )
