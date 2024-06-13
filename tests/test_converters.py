"""Test converters module for SMufoLib."""

import unittest
from smufolib import converters

# pylint: disable=missing-function-docstring, invalid-name


class Converters(unittest.TestCase):
    def test_convertMeasurement(self):
        self.assertEqual(converters.convertMeasurement(
            125, convertTo='spaces', unitsPerEm=1000), 0.5)
        self.assertEqual(converters.convertMeasurement(
            0.5, convertTo='units', unitsPerEm=1000), 125)
        with self.assertRaises(TypeError):
            converters.convertMeasurement(
                (125,), convertTo='spaces', unitsPerEm=1000)
        with self.assertRaises(ValueError):
            converters.convertMeasurement(
                125, convertTo='something else', unitsPerEm=1000)

    def test_toDecimal(self):
        for value in ('U+E00C', 'uE00C', 'uniE00C'):
            self.assertEqual(converters.toDecimal(value), 57356)
            with self.assertRaises(ValueError):
                converters.toDecimal(value[1:])
        with self.assertRaises(TypeError):
            converters.toDecimal(57356)


# def testToUniHex():
#     for value in (57344, '57344'):
#         assert converters.toUniHex(value) == 'U+E000'

#     with pytest.raises(ValueError):
#         converters.toUniHex('23a45')


# def testToUniName():
#     for value in (57344, '57344', 'U+E000'):
#         assert converters.toUniName(value, short=False) == 'uniE000'
#         assert converters.toUniName(value, short=True) == 'uE000'

#     with pytest.raises(ValueError):
#         for value in ('U+ E000', 'U+E0G0'):
#             converters.toUniName(value)

if __name__ == '__main__':
    unittest.main()
