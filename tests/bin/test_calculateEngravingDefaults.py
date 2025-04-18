import json
import sys
import unittest
from unittest.mock import patch

from tests.testUtils import (
    SavedFontMixin,
    SuppressOutputMixin,
    drawCircle,
    drawLines,
    getVerboseOutput,
)
from bin.calculateEngravingDefaults import (
    MAPPING,
    calculateEngravingDefaults,
    main,
    boundsHeight,
    boundsLeft,
    stemDot,
    xInner,
    xOrigin,
    yInner,
    yMinimum,
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
        # pylint: enable=E1101

        self.font.info.familyName = "testFont"
        self.font.info.unitsPerEm = 1000
        for attribute, mapping in MAPPING.items():
            if attribute == "textFontFamily":
                continue
            name = mapping["glyph"]
            glyph = self.font.newGlyph(name)
            drawLines(glyph, ((10, 0), (20, 0), (20, 15), (10, 15)))

        self.fontPath = self.saveFontToTemp()

    def test_calculateEngravingDefaults_basic(self):
        calculateEngravingDefaults(self.font)
        ed = self.font.smufl.engravingDefaults
        self.assertTrue(hasattr(ed, "tupletBracketThickness"))
        self.assertIsInstance(ed.tupletBracketThickness, (int, float))

    def test_calculateEngravingDefaults_exclude(self):
        calculateEngravingDefaults(self.font, exclude=["arrowShaftThickness"])
        ed = self.font.smufl.engravingDefaults
        self.assertIsNone(ed.arrowShaftThickness)

    def test_calculateEngravingDefaults_override(self):
        override = {"arrowShaftThickness": 1234, "textFontFamily": ("font1", "font2")}
        calculateEngravingDefaults(self.font, override=override)
        self.assertEqual(self.font.smufl.engravingDefaults.arrowShaftThickness, 1234)

    def test_calculateEngravingDefaults_remap(self):
        remapGlyph = self.font.newGlyph("testGlyph")
        drawLines(remapGlyph, ((0, 0), (0, 7), (7, 7), (7, 0)))
        remap = {
            "arrowShaftThickness": {
                "ruler": "boundsHeight",
                "glyph": "testGlyph",
                "referenceIndex": None,
            }
        }
        calculateEngravingDefaults(self.font, remap=remap)
        self.assertIsNotNone(self.font.smufl.engravingDefaults.arrowShaftThickness)

    @patch("builtins.print")
    def test_calculateEngravingDefaults_remap_with_nonexistent(self, mock_print):
        remap = {
            "arrowShaftThickness": {
                "ruler": "boundsHeight",
                "glyph": "testGlyph",  # Reference non-existent glyph
                "referenceIndex": None,
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
        self.assertIsNotNone(self.font.smufl.engravingDefaults.arrowShaftThickness)

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

    def test_boundsHeight(self):
        drawLines(self.glyph, ((10, 0), (20, 0), (20, 15), (10, 15)))
        result = boundsHeight(self.glyph)
        self.assertEqual(result, 15)

    def test_boundsLeft(self):
        drawLines(self.glyph, ((10, 0), (20, 0), (20, 15), (10, 15)))
        result = boundsLeft(self.glyph)
        self.assertEqual(result, 10)

    def test_stemDot(self):
        drawLines(self.glyph, ((0, 0), (10, 0), (10, 20), (0, 20)))
        drawCircle(self.glyph, (30, 10), 10)
        result = stemDot(self.glyph)
        self.assertEqual(result, 10)

    def test_stemDot_with_missing_lines(self):
        drawCircle(self.glyph, (30, 10), 10)
        result = stemDot(self.glyph)
        self.assertIsNone(result)

    def test_stemDot_with_missing_curves(self):
        drawLines(self.glyph, ((0, 0), (10, 0), (10, 20), (0, 20)))
        result = stemDot(self.glyph)
        self.assertIsNone(result)

    def test_stemDot_with_same_contour_index(self):
        self.contour.appendPoint((10, 20), "curve")
        self.contour.appendPoint((12, 20), "line")
        self.glyph.appendContour(self.contour)
        result = stemDot(self.glyph)
        self.assertIsNone(result)

    def test_xInner(self):
        drawLines(self.glyph, ((0, 0), (10, 0), (10, 20), (0, 20)))
        drawLines(self.glyph, ((20, 0), (30, 0), (30, 20), (20, 20)))
        result = xInner(self.glyph, referenceIndex=3)
        self.assertEqual(result, 10)

    def test_xInner_with_same_contour_index(self):
        self.contour.appendPoint((10, 20), "curve")
        self.contour.appendPoint((12, 20), "line")
        self.glyph.appendContour(self.contour)
        result = xInner(self.glyph)
        self.assertIsNone(result)

    def test_xInner_with_non_adjacent_y(self):
        drawLines(self.glyph, ((20, 20), (30, 30), (30, 40), (20, 40)))
        drawLines(self.glyph, ((0, 0), (30, 0), (30, 20), (20, 20)))
        result = xInner(self.glyph, referenceIndex=3)
        self.assertEqual(result, 0)

    def test_xOrigin(self):
        drawLines(self.glyph, ((10, 0), (20, 0), (20, 15), (10, 15)))
        result = xOrigin(self.glyph)
        self.assertEqual(result, 10)

    def test_xOrigin_with_same_point_position(self):
        self.contour.appendPoint((10, 20), "curve")
        self.contour.appendPoint((10, 20), "line")
        self.glyph.appendContour(self.contour)
        result = xOrigin(self.glyph)
        self.assertIsNone(result)

    def test_yInner(self):
        drawLines(self.glyph, ((0, 0), (20, 0), (20, 10), (0, 10)))
        drawLines(self.glyph, ((0, 20), (20, 20), (20, 30), (0, 30)))
        result = yInner(self.glyph, referenceIndex=3)
        self.assertEqual(result, 10)

    def test_yInner_with_same_contour_index(self):
        self.contour.appendPoint((10, 20), "curve")
        self.contour.appendPoint((12, 20), "line")
        self.glyph.appendContour(self.contour)
        result = yInner(self.glyph)
        self.assertIsNone(result)

    def test_yMinimum(self):
        drawLines(self.glyph, ((0, 0), (20, 0), (20, 10), (0, 10)))
        drawLines(self.glyph, ((0, 20), (20, 20), (20, 30), (0, 30)))
        result = yMinimum(self.glyph, referenceIndex=3)
        self.assertEqual(result, 10)

    def test_yMinimum_with_same_contour_index(self):
        self.contour.appendPoint((10, 20), "curve")
        self.contour.appendPoint((12, 20), "line")
        self.glyph.appendContour(self.contour)
        result = yMinimum(self.glyph)
        self.assertIsNone(result)

    @patch("bin.calculateEngravingDefaults.calculateEngravingDefaults")
    def test_main(self, mock_calculateEngravingDefaults):
        override = {"tupletBracketThickness": 0.5}
        remap = {
            "tupletBracketThickness": {
                "ruler": "boundsHeight",
                "glyph": "noteheadBlack",
                "referenceIndex": 0,
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
