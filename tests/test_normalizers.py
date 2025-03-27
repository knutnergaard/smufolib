import unittest
from smufolib import Font, Glyph
from smufolib.normalizers import (
    normalizeFont,
    normalizeClasses,
    normalizeDescription,
    normalizeDesignSize,
    normalizeSizeRange,
    normalizeSmufl,
    normalizeSmuflName,
    normalizeEngravingDefaults,
    normalizeEngravingDefaultsAttr,
    normalizeRequest,
    normalizeRequestPath,
)


class Normalizers(unittest.TestCase):
    faultyNames = ["", "smufl-name42", "SmuflName42"]
    font = Font()
    for name in ["uniE001", "uniE002", "uniE003", "uniE004"]:
        font[name] = Glyph()

    def test_normalizeFont_with_invalid_type(self):
        glyph = self.font["uniE001"]
        with self.assertRaises(TypeError):
            normalizeFont(glyph)

    def test_normalizeClasses_with_valid_input(self):
        self.assertEqual(normalizeClasses(["className"]), ("className",))

    def test_normalizeClasses_with_invalid_type(self):
        with self.assertRaises(TypeError):
            normalizeClasses("className")

    def test_normalizeClasses_with_invalid_values(self):
        for faulty_value in [
            [None],
            ["className", "className"],
            [""],
            ["smufl-name42"],
            ["SmuflName42"],
        ]:
            with self.assertRaises(ValueError):
                normalizeClasses(faulty_value)

    def test_normalizeDescription_with_invalid_type(self):
        with self.assertRaises(TypeError):
            normalizeDescription(0)

    def test_normalizeDescription_with_invalid_value(self):
        with self.assertRaises(ValueError):
            normalizeDescription("")

    def test_normalizeDesignSize_with_invalid_type(self):
        with self.assertRaises(TypeError):
            normalizeDesignSize("24")

    def test_normalizeDesignSize_with_invalid_value(self):
        with self.assertRaises(ValueError):
            normalizeDesignSize(9)

    def test_normalizeSizeRange_with_valid_input(self):
        self.assertEqual(normalizeSizeRange([10, 36]), (10, 36))

    def test_normalizeSizeRange_with_invalid_type(self):
        with self.assertRaises(TypeError):
            normalizeSizeRange(10)

    def test_normalizeSizeRange_with_invalid_values(self):
        for faulty_value in [[24], [36, 10], [9, 36]]:
            with self.assertRaises(ValueError):
                normalizeSizeRange(faulty_value)

    def test_normalizeSmufl_with_invalid_type(self):
        with self.assertRaises(TypeError):
            normalizeSmufl(self.font)

    def test_normalizeSmuflName_with_invalid_type(self):
        with self.assertRaises(TypeError):
            normalizeSmuflName(0)

    def test_normalizeSmuflName_with_invalid_values(self):
        for name in self.faultyNames:
            with self.assertRaises(ValueError):
                normalizeSmuflName(name)

    def test_normalizeEngravingDefaults_with_invalid_type(self):
        with self.assertRaises(TypeError):
            normalizeEngravingDefaults(self.font)

    def test_normalizeEngravingDefaultsAttr_with_invalid_values(self):
        for wrongAttr, wrongVal in [
            ("attribute", "23"),
            ("attribute", [23]),
            ("textFontFamily", [23]),
        ]:
            with self.assertRaises((TypeError, AttributeError, ValueError)):
                normalizeEngravingDefaultsAttr(wrongAttr, wrongVal)
        with self.assertRaises(ValueError):
            normalizeEngravingDefaultsAttr("textFontFamily", [""])

    def test_normalizeRequest_with_invalid_type(self):
        with self.assertRaises(TypeError):
            normalizeRequest("path")

    def test_normalizeRequestPath_with_invalid_type(self):
        with self.assertRaises(TypeError):
            normalizeRequestPath(["path"], parameter="path")
