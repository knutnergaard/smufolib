import json
import sys
import unittest
from unittest.mock import PropertyMock, patch


from tests.testUtils import (
    SavedFontMixin,
    SuppressOutputMixin,
    drawLines,
    getVerboseOutput,
)
from smufolib.objects.engravingDefaults import EngravingDefaults
from bin.calculateEngravingDefaults import (
    ENGRAVING_DEFAULTS_MAPPING,
    calculateEngravingDefaults,
    main,
)


class TestCalculateEngravingDefaults(
    SavedFontMixin, SuppressOutputMixin, unittest.TestCase
):
    def setUp(self):
        super().setUp()
        self.suppressOutput()

        # pylint: disable=E1101
        self.font, _ = self.objectGenerator("font")
        self.glyph, _ = self.objectGenerator("glyph")
        self.contour, _ = self.objectGenerator("contour")
        self.otherContour, _ = self.objectGenerator("contour")

        self.font.info.familyName = "testFont"
        self.font.info.unitsPerEm = 1000
        for attribute, mapping in ENGRAVING_DEFAULTS_MAPPING.items():
            if attribute == "textFontFamily":
                continue
            name = mapping["glyph"]
            glyph = self.font.newGlyph(name)
            drawLines(glyph, ((10, 0), (20, 0), (20, 15), (10, 15)))

        self.fontPath = self.saveFontToTemp()
        self.ed = self.font.smufl.engravingDefaults

    def test_calculateEngravingDefaults_basic(self):
        calculateEngravingDefaults(self.font)
        self.assertTrue(hasattr(self.ed, "tupletBracketThickness"))
        self.assertIsInstance(self.ed.tupletBracketThickness, (int, float))

    def test_calculateEngravingDefaults_exclude(self):
        self.ed.auto = False
        calculateEngravingDefaults(self.font, exclude=["arrowShaftThickness"])
        self.assertIsNone(self.ed.arrowShaftThickness)

    def test_calculateEngravingDefaults_override(self):
        override = {"arrowShaftThickness": 1234, "textFontFamily": ("font1", "font2")}
        calculateEngravingDefaults(self.font, override=override)
        self.assertEqual(self.ed.arrowShaftThickness, 1234)

    def test_calculateEngravingDefaults_remap(self):
        remapGlyph = self.font.newGlyph("testGlyph")
        drawLines(remapGlyph, ((0, 0), (0, 7), (7, 7), (7, 0)))
        remap = {
            "arrowShaftThickness": {
                "ruler": "glyphBoundsHeight",
                "glyph": "testGlyph",
            }
        }
        calculateEngravingDefaults(self.font, remap=remap)
        self.assertIsNotNone(self.ed.arrowShaftThickness)

    @patch("builtins.print")
    def test_calculateEngravingDefaults_remap_with_nonexistent(self, mock_print):
        remap = {
            "arrowShaftThickness": {
                "ruler": "glyphBoundsHeight",
                "glyph": "testGlyph",  # Reference non-existent glyph
            }
        }
        calculateEngravingDefaults(self.font, verbose=True, remap=remap)
        mock_print.assert_any_call(
            "Skipping attribute assigned to non-existent glyph: "
            "'arrowShaftThickness' ('testGlyph')"
        )

    def test_calculateEngravingDefaults_spaces(self):
        self.font.smufl.staffSpaces = 200  # units per space
        calculateEngravingDefaults(self.font, spaces=True)
        self.assertIsNotNone(self.ed.arrowShaftThickness)

    @patch("bin.calculateEngravingDefaults.Font.save")
    def test_calculateEngravingDefaults_calls_save(self, mock_save):
        calculateEngravingDefaults(self.font)
        mock_save.assert_called_once()

    def test_calculateEngravingDefaults_verbose(self):
        output = getVerboseOutput(
            calculateEngravingDefaults,
            font=self.font,
            verbose=True,
            exclude=["textFontFamily"],
        )
        self.assertIn("Setting attributes:", output)
        self.assertIn("'stemThickness':", output)
        self.assertIn("Done!", output)

    @patch("bin.calculateEngravingDefaults.calculateEngravingDefaults")
    def test_main(self, mock_calculateEngravingDefaults):
        override = {"tupletBracketThickness": 0.5}
        remap = {
            "tupletBracketThickness": {
                "ruler": "glyphBoundsHeight",
                "glyph": "noteheadBlack",
            }
        }

        test_args = [
            "calculateEngravingDefaults",
            str(self.fontPath),
            "--override",
            json.dumps(override),
            "--remap",
            json.dumps(remap),
            "--exclude",
            "textFontFamily",
            "--spaces",
            "--verbose",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        mock_calculateEngravingDefaults.assert_called_once()
        args, kwargs = mock_calculateEngravingDefaults.call_args
        self.assertIsInstance(args[0], type(self.font))
        self.assertEqual(kwargs["exclude"], ["textFontFamily"])
        self.assertEqual(kwargs["override"], override)
        self.assertEqual(kwargs["remap"], remap)
        self.assertTrue(kwargs["spaces"])
        self.assertTrue(kwargs["verbose"])
