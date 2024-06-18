import unittest
from smufolib.pointUtils import (
    Point,
    Position,
    getPoints,
    getContourPoints,
    getCompositePoints
)

# pylint: disable=C0115, C0116, C0103


class PointUtils(unittest.TestCase):

    def setUp(self):
        self.position1 = Position(0.0, 0.0)
        self.position2 = Position(0.0, 0.0)
        self.position3 = Position(0.0, 0.0)
        self.point1 = Point(self.position1, 'line', 0)
        self.point2 = Point(self.position2, 'curve', 0)
        self.point3 = Point(self.position2, 'qcurve', 0)

    def tearDown(self):
        pass

    def test_getPoints(self):
        pass

    def test_getContourPoints(self):
        pass

    def test_getCompositePoints(self):
        pass


if __name__ == '__main__':
    unittest.main()
