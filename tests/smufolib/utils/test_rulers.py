import unittest

from smufolib.utils.rulers import (
    glyphBoundsHeight,
    glyphBoundsWidth,
    glyphBoundsXMinAbs,
    xDistanceStemToDot,
    xDistanceBetweenContours,
    yDistanceBetweenContours,
    xStrokeWidthAtOrigin,
    yStrokeWidthAtMinimum,
    wedgeArmStrokeWidth,
    getGlyphContours,
    hasHorizontalOffCurve,
    hasVerticalOffCurve,
)
from tests.testUtils import SavedFontMixin, SavedMetadataMixin, drawLines, drawCircle


class TestRulers(SavedFontMixin, SavedMetadataMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.font, _ = self.objectGenerator("font")  # pylint: disable=E1101
        self.glyph = self.font.newGlyph("testGlyph")
        self.contour, _ = self.objectGenerator("contour")  # pylint: disable=E1101

    def test_glyphBoundsHeight_basic(self):
        drawLines(self.glyph, ((10, 0), (20, 0), (20, 15), (10, 15)))
        result = glyphBoundsHeight(self.glyph)
        self.assertEqual(result, 15)

    def test_glyphBoundsHeight_no_bounds(self):
        result = glyphBoundsHeight(self.glyph)
        self.assertIsNone(result)

    def test_glyphBoundsWidth_basic(self):
        drawLines(self.glyph, ((10, 0), (20, 0), (20, 15), (10, 15)))
        result = glyphBoundsWidth(self.glyph)
        self.assertEqual(result, 10)

    def test_glyphBoundsWidth_no_bounds(self):
        result = glyphBoundsWidth(self.glyph)
        self.assertIsNone(result)

    def test_glyphBoundsXMinAbs_basic(self):
        drawLines(self.glyph, ((10, 0), (20, 0), (20, 15), (10, 15)))
        result = glyphBoundsXMinAbs(self.glyph)
        self.assertEqual(result, 10)

    def test_glyphBoundsXMinAbs_no_bounds(self):
        result = glyphBoundsXMinAbs(self.glyph)
        self.assertIsNone(result)

    def test_xDistanceStemToDot_stem_dot(self):
        drawLines(self.glyph, ((0, 0), (10, 0), (10, 20), (0, 20)))
        drawCircle(self.glyph, (30, 10), 10)
        result = xDistanceStemToDot(self.glyph)
        self.assertEqual(result, 10)

    def test_xDistanceStemToDot_dot_stem(self):
        drawLines(self.glyph, ((30, 0), (40, 0), (40, 20), (30, 20)))
        drawCircle(self.glyph, (10, 10), 10)
        result = xDistanceStemToDot(self.glyph)
        self.assertEqual(result, 10)

    def test_xDistanceStemToDot_with_missing_lines(self):
        drawCircle(self.glyph, (30, 10), 10)
        result = xDistanceStemToDot(self.glyph)
        self.assertIsNone(result)

    def test_xDistanceStemToDot_with_missing_curves(self):
        drawLines(self.glyph, ((0, 0), (10, 0), (10, 20), (0, 20)))
        result = xDistanceStemToDot(self.glyph)
        self.assertIsNone(result)

    def test_xDistanceBetweenContours_basic(self):
        drawLines(self.glyph, ((0, 0), (10, 0), (10, 20), (0, 20)))
        drawLines(self.glyph, ((20, 0), (30, 0), (30, 20), (20, 20)))
        result = xDistanceBetweenContours(self.glyph)
        self.assertEqual(result, 10)

    def test_xDistanceBetweenContours_no_points(self):
        result = xDistanceBetweenContours(self.glyph)
        self.assertIsNone(result)

    def test_xDistanceBetweenContours_same_contour_index(self):
        self.contour.appendPoint((10, 20), "curve")
        self.contour.appendPoint((12, 20), "line")
        self.glyph.appendContour(self.contour)
        result = xDistanceBetweenContours(self.glyph)
        self.assertIsNone(result)

    def test_yDistanceBetweenContours_basic(self):
        drawLines(self.glyph, ((0, 0), (20, 0), (20, 10), (0, 10)))
        drawLines(self.glyph, ((0, 20), (20, 20), (20, 30), (0, 30)))
        result = yDistanceBetweenContours(self.glyph)
        self.assertEqual(result, 10)

    def test_yDistanceBetweenContours_no_points(self):
        result = yDistanceBetweenContours(self.glyph)
        self.assertIsNone(result)

    def test_yDistanceBetweenContours_same_contour_index(self):
        self.contour.appendPoint((10, 20), "curve")
        self.contour.appendPoint((12, 20), "line")
        self.glyph.appendContour(self.contour)
        result = yDistanceBetweenContours(self.glyph)
        self.assertIsNone(result)

    def test_xStrokeWidthAtOrigin_basic(self):
        drawLines(self.glyph, ((10, 0), (20, 0), (20, 15), (10, 15)))
        result = xStrokeWidthAtOrigin(self.glyph)
        self.assertEqual(result, 10)

    def test_xStrokeWidthAtOrigin_no_points(self):
        result = xStrokeWidthAtOrigin(self.glyph)
        self.assertIsNone(result)

    def test_xStrokeWidthAtOrigin_different_contour_index(self):
        drawLines(self.glyph, ((0, 20), (20, 0), (20, 10), (0, 10)))
        drawLines(self.glyph, ((5, 10), (20, 20), (20, 30), (0, 30)))
        result = xStrokeWidthAtOrigin(self.glyph)
        self.assertEqual(result, 20)

    def test_xStrokeWidthAtOrigin_same_point_position(self):
        self.contour.appendPoint((10, 20), "curve")
        self.contour.appendPoint((10, 20), "line")
        self.glyph.appendContour(self.contour)
        result = xStrokeWidthAtOrigin(self.glyph)
        self.assertIsNone(result)

    def test_yStrokeWidthAtMinimum_basic(self):
        drawLines(self.glyph, ((0, 10), (0, 20), (15, 20), (15, 10)))
        result = yStrokeWidthAtMinimum(self.glyph)
        self.assertEqual(result, 10)

    def test_yStrokeWidthAtMinimum_no_points(self):
        result = yStrokeWidthAtMinimum(self.glyph)
        self.assertIsNone(result)

    def test_yStrokeWidthAtMinimum_different_contour_index(self):
        drawLines(self.glyph, ((20, 0), (0, 20), (10, 20), (10, 0)))
        drawLines(self.glyph, ((10, 5), (20, 20), (30, 20), (30, 0)))
        result = yStrokeWidthAtMinimum(self.glyph)
        self.assertEqual(result, 20)

    def test_yStrokeWidthAtMinimum_points_misaligned(self):
        drawLines(self.glyph, ((0, 10), (10, 20), (15, 20), (25, 10)))
        result = yStrokeWidthAtMinimum(self.glyph)
        self.assertIsNone(result)

    def test_wedgeArmStrokeWidth(self):
        drawLines(
            self.glyph,
            (
                (
                    (0, 130),
                    (750, 23),
                    (750, 55),
                    (115, 146),
                    (750, 237),
                    (750, 269),
                    (0, 162),
                )
            ),
        )
        result = wedgeArmStrokeWidth(self.glyph)
        self.assertEqual(result, 32)

    def test_getGlyphContours(self):
        referencedGlyph = self.font.newGlyph("referencedGlyph")
        drawLines(referencedGlyph, ((10, 0), (20, 0), (20, 15), (10, 15)))
        self.glyph.appendComponent("referencedGlyph", offset=(1, 1))
        drawLines(self.glyph, ((10, 0), (20, 0), (20, 15), (10, 15)))
        result = tuple(getGlyphContours(self.glyph))
        self.assertEqual(len(result), 2)

    def test_hasHorizontalOffCurve_basic(self):
        drawCircle(self.glyph, (10, 10), 10)
        contour = self.glyph.contours[0]
        curves = [p for s in contour for p in s if p.type == "curve"]
        top = next(p for p in curves if p.y > 15)
        bottom = next(p for p in curves if p.y < 5)
        left = next(p for p in curves if p.x < 5)
        right = next(p for p in curves if p.x > 15)

        self.assertTrue(hasHorizontalOffCurve(top))
        self.assertTrue(hasHorizontalOffCurve(bottom))
        self.assertFalse(hasHorizontalOffCurve(left))
        self.assertFalse(hasHorizontalOffCurve(right))

    def test_hasHorizontalOffCurve_not_curve(self):
        drawLines(self.glyph, ((10, 0), (20, 0), (20, 15), (10, 15)))
        contour = self.glyph.contours[0]
        self.assertFalse(hasHorizontalOffCurve(contour.points[0]))

    def test_hasVerticalOffCurve_basic(self):
        drawCircle(self.glyph, (10, 10), 10)
        contour = self.glyph.contours[0]
        curves = [p for s in contour for p in s if p.type == "curve"]
        top = next(p for p in curves if p.y > 15)
        bottom = next(p for p in curves if p.y < 5)
        left = next(p for p in curves if p.x < 5)
        right = next(p for p in curves if p.x > 15)

        self.assertFalse(hasVerticalOffCurve(top))
        self.assertFalse(hasVerticalOffCurve(bottom))
        self.assertTrue(hasVerticalOffCurve(left))
        self.assertTrue(hasVerticalOffCurve(right))

    def test_hasVerticalOffCurve_not_curve(self):
        drawLines(self.glyph, ((10, 0), (20, 0), (20, 15), (10, 15)))
        contour = self.glyph.contours[0]
        self.assertFalse(hasVerticalOffCurve(contour.points[0]))
