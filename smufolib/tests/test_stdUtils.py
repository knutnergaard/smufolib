import unittest
from smufolib.stdUtils import flatten, addTuples, isFloat, validateClassAttr

# pylint: disable=C0115, C0116, C0103


class StdUtils(unittest.TestCase):
    def test_flatten(self):
        matrix = [[[i for i in range(5)] for j in range(5)] for h in range(5)]
        self.assertEqual(list(flatten(matrix)), list(range(5)) * 25)
        self.assertEqual(
            list(flatten(matrix, 1)), [[i for i in range(5)] for j in range(25)]
        )

    def test_addTuples(self):
        self.assertEqual(addTuples((2, 4), (2, 4)), (4, 8))

    def test_isFloat(self):
        self.assertTrue(isFloat("1.2"))
        self.assertFalse(isFloat("1"))

    def test_validateClassAttr(self):
        with self.assertRaises(TypeError):
            validateClassAttr(object, 42)
