import unittest
from smufolib.utils.pointUtils import (
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

        self.glyph3 = self.font.newGlyph("testGlyph3")
        self.addContour(self.glyph3, (9, 10), (11, 12))

        self.component1 = self.glyph1.appendComponent("testGlyph2", offset=(1, 1))
        self.component2 = self.glyph2.appendComponent("testGlyph3", offset=(1, 1))

        # Expected points for contour and composite tests
        self.expectedContourPoints1 = (
            Point("line", position=Position(1, 2), contourIndex=0),
            Point("line", position=Position(3, 4), contourIndex=0),
        )

        self.expectedContourPoints2 = (
            Point("line", position=Position(5, 6), contourIndex=0),
            Point("line", position=Position(7, 8), contourIndex=0),
        )

        self.expectedContourPoints3 = (
            Point("line", position=Position(9, 10), contourIndex=0),
            Point("line", position=Position(11, 12), contourIndex=0),
        )

        self.expectedCompositePoints1 = (
            Point("line", position=Position(6, 7), contourIndex=0),  # (5+1, 6+1)
            Point("line", position=Position(8, 9), contourIndex=0),  # (7+1, 8+1)
        )

        self.expectedCompositePoints2 = (
            Point("line", position=Position(10, 11), contourIndex=0),  # (9+1, 10+1)
            Point("line", position=Position(12, 13), contourIndex=0),  # (11+1, 12+1)
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

    def test_getPoints_with_font(self):
        points = tuple(getPoints(self.font))
        expectedPoints = (
            self.expectedContourPoints1
            + self.expectedContourPoints2
            + self.expectedContourPoints3
            + self.expectedCompositePoints1
            + self.expectedCompositePoints2
        )
        self.assertPointListsEqual(points, expectedPoints)

    def test_getPoints_with_glyph(self):
        points = tuple(getPoints(self.glyph1))
        expectedPoints = self.expectedContourPoints1 + self.expectedCompositePoints1
        self.assertPointListsEqual(points, expectedPoints)
        assert isinstance(points, tuple)

    def test_getPoints_with_tuple_of_glyphs(self):
        points = tuple(getPoints((self.glyph1, self.glyph2)))
        assert isinstance(points, tuple)

    def test_getContourPoints_with_glyph(self):
        points = tuple(getContourPoints(self.glyph1))
        self.assertPointListsEqual(points, self.expectedContourPoints1)

    def test_getContourPoints_with_contour(self):
        points = tuple(getContourPoints(self.glyph1.contours[0]))
        assert isinstance(points, tuple)

    def test_getContourPoints_with_tuple_of_contours(self):
        points = tuple(getContourPoints(self.glyph1.contours))
        assert isinstance(points, tuple)

    def test_getContourPoints_with_font(self):
        points = tuple(getContourPoints(self.font))
        expectedPoints = (
            self.expectedContourPoints1
            + self.expectedContourPoints2
            + self.expectedContourPoints3
        )
        self.assertPointListsEqual(points, expectedPoints)

    def test_getCompositePoints_with_glyph(self):
        points = tuple(getCompositePoints(self.glyph1))
        self.assertPointListsEqual(points, self.expectedCompositePoints1)
        assert isinstance(points, tuple)

    def test_getCompositePoints_with_component(self):
        points = tuple(getCompositePoints(self.component1))
        assert isinstance(points, tuple)

    def test_getCompositePoints_with_tuple_of_components(self):
        points = tuple(getCompositePoints((self.component1, self.component2)))
        assert isinstance(points, tuple)

    def test_getCompositePoints_with_font(self):
        points = tuple(getCompositePoints(self.font))
        expectedPoints = self.expectedCompositePoints1 + self.expectedCompositePoints2
        self.assertPointListsEqual(points, expectedPoints)

    def test_getCompositePoints_invalid_obj_type(self):
        with self.assertRaises(TypeError):
            getCompositePoints("invalid_type")

    def test_getCompositePoints_invalid_types_value(self):
        result = getCompositePoints(self.component1, types="invalidType")
        self.assertTupleEqual(tuple(result), ())
