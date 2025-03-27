import unittest
from smufolib.pointUtils import (
    Point,
    Position,
    getPoints,
    getContourPoints,
    getCompositePoints,
)


class TestPointUtils(unittest.TestCase):
    def setUp(self):
        self.font, _ = self.objectGenerator("font")  # pylint: disable=E1101
        self.layer = self.font.newLayer("testLayer")
        self.font.defaultLayer = self.layer
        self.glyph1 = self.font.newGlyph("testGlyph1")
        self.addContour(self.glyph1, (1, 2), (3, 4))
        self.glyph2 = self.font.newGlyph("testGlyph2")
        self.addContour(self.glyph2, (5, 6), (7, 8))
        self.component = self.glyph1.appendComponent("testGlyph2", offset=(1, 1))

        # Expected points for contour and composite tests
        self.expectedContourPoints1 = (
            Point("line", position=Position(1, 2), contourIndex=0),
            Point("line", position=Position(3, 4), contourIndex=0),
        )

        self.expectedContourPoints2 = (
            Point("line", position=Position(5, 6), contourIndex=0),
            Point("line", position=Position(7, 8), contourIndex=0),
        )

        self.expectedCompositePoints = (
            Point("line", position=Position(6, 7), contourIndex=0),  # (5+1, 6+1)
            Point("line", position=Position(8, 9), contourIndex=0),  # (7+1, 8+1)
        )

    def addContour(self, glyph, *points):
        pen = glyph.getPen()
        pen.moveTo(points[0])
        for point in points[1:]:
            pen.lineTo(point)
        pen.closePath()

    def assertPointListsEqual(self, actual, expected):
        self.assertCountEqual(actual, expected)
        for point in actual:
            self.assertIsInstance(point, Point)
            self.assertIsInstance(point.position, Position)

    def test_getContourPoints_with_glyph(self):
        points = tuple(getContourPoints(self.glyph1))
        self.assertPointListsEqual(points, self.expectedContourPoints1)

    def test_getCompositePoints_with_glyph(self):
        points = tuple(getCompositePoints(self.glyph1))
        self.assertPointListsEqual(points, self.expectedCompositePoints)

    def test_getPoints_with_glyph(self):
        points = tuple(getPoints(self.glyph1))
        expectedPoints = self.expectedContourPoints1 + self.expectedCompositePoints
        self.assertPointListsEqual(points, expectedPoints)

    def test_getContourPoints_with_font(self):
        points = tuple(getContourPoints(self.font))
        expectedPoints = self.expectedContourPoints1 + self.expectedContourPoints2
        self.assertPointListsEqual(points, expectedPoints)

    def test_getCompositePoints_with_font(self):
        points = tuple(getCompositePoints(self.font))
        self.assertPointListsEqual(points, self.expectedCompositePoints)

    def test_getPoints_with_font(self):
        points = tuple(getPoints(self.font))
        expectedPoints = (
            self.expectedContourPoints1
            + self.expectedContourPoints2
            + self.expectedCompositePoints
        )
        self.assertPointListsEqual(points, expectedPoints)
