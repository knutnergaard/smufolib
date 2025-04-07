import unittest
from smufolib.converters import (
    convertMeasurement,
    toDecimal,
    toUniHex,
    toUniName,
    toKebab,
    toNumber,
    toIntIfWhole,
)

# pylint: disable=C0115, C0116, C0103


class Converters(unittest.TestCase):
    def test_convertMeasurement(self):
        self.assertEqual(
            convertMeasurement(125, targetUnit="spaces", unitsPerEm=1000), 0.5
        )
        self.assertEqual(
            convertMeasurement(0.5, targetUnit="units", unitsPerEm=1000), 125
        )

        with self.assertRaises(TypeError):
            convertMeasurement((125,), targetUnit="spaces", unitsPerEm=1000)
        with self.assertRaises(ValueError):
            convertMeasurement(125, targetUnit="something else", unitsPerEm=1000)

    def test_toDecimal(self):
        for prefix in ("U+", "u", "uni"):
            value = f"{prefix}E00C"
            self.assertEqual(toDecimal(value), 57356)
            with self.assertRaises(ValueError):
                toDecimal(value[1:])
            with self.assertRaises(ValueError):
                toDecimal(f"{prefix}110000")

        with self.assertRaises(TypeError):
            toDecimal(57356)

    def test_toUniHex(self):
        self.assertEqual(toUniHex(57344), "U+E000")
        with self.assertRaises(TypeError):
            toUniHex("57344")
        with self.assertRaises(ValueError):
            toUniHex(2000000)

    def test_toUniName(self):
        self.assertEqual(toUniName(57344), "uniE000")
        self.assertEqual(toUniName("U+E000"), "uniE000")
        self.assertEqual(toUniName(57344, short=True), "uE000")
        with self.assertRaises(TypeError):
            toUniName([57344])
        with self.assertRaises(ValueError):
            toUniName("57344")
        with self.assertRaises(ValueError):
            toUniName(2000000)

    def test_toKebab(self):
        self.assertEqual(toKebab("helloWorld!"), "hello-world!")
        # self.assertEqual(toKebab('setID'), 'set-id')
        with self.assertRaises(TypeError):
            toKebab(["485937"])

    def test_toNumber(self):
        self.assertEqual(toNumber("4598"), 4598)
        self.assertEqual(toNumber("0x4598"), 0x4598)
        self.assertEqual(toNumber("45.8"), 45.8)
        with self.assertRaises(TypeError):
            toNumber(["485937"])
        with self.assertRaises(ValueError):
            toNumber("456h")

    def test_toIntIfWhole(self):
        self.assertEqual(toIntIfWhole(10), 10)
        self.assertEqual(toIntIfWhole(-5), -5)

        self.assertEqual(toIntIfWhole(10.0), 10)
        self.assertEqual(toIntIfWhole(-5.0), -5)

        self.assertEqual(toIntIfWhole(10.1), 10.1)
        self.assertEqual(toIntIfWhole(-5.9), -5.9)

        self.assertEqual(toIntIfWhole(0.0), 0)
        self.assertEqual(toIntIfWhole(-0.0), 0)
        self.assertEqual(toIntIfWhole(1.0000000000001), 1.0000000000001)
        self.assertEqual(toIntIfWhole(1.9999999999999), 1.9999999999999)
