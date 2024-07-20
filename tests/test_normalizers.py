import unittest
from smufolib import Font, Glyph, EngravingDefaults
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
    normalizeRequestPath
)

# pylint: disable=C0115, C0116, C0103


class Normalizers(unittest.TestCase):
    faultyNames = ['', 'smufl-name42', 'SmuflName42']
    font = Font()
    for name in ['uniE001', 'uniE002', 'uniE003', 'uniE004']:
        font[name] = Glyph()

    def test_normalizeFont(self):
        glyph = self.font['uniE001']
        with self.assertRaises(TypeError):
            normalizeFont(glyph)

    def test_normalizeClasses(self):
        self.assertEqual(normalizeClasses(['className']), ('className',))
        with self.assertRaises(TypeError):
            normalizeClasses('className')
        for faultyValue in [
            [None],
            ['className', 'className'],
            [''],
            ['smufl-name42'],
                ['SmuflName42']]:
            with self.assertRaises(ValueError):
                normalizeClasses(faultyValue)

    def test_normalizeDescription(self):
        with self.assertRaises(TypeError):
            normalizeDescription(0)
        with self.assertRaises(ValueError):
            normalizeDescription('')

    def test_normalizeDesignSize(self):
        with self.assertRaises(TypeError):
            normalizeDesignSize('24')
        with self.assertRaises(ValueError):
            normalizeDesignSize(9)

    def test_normalizeSizeRange(self):
        self.assertEqual(normalizeSizeRange([10, 36]), (10, 36))
        with self.assertRaises(TypeError):
            normalizeSizeRange(10)
        for faultyValue in [[24], [36, 10], [9, 36]]:
            with self.assertRaises(ValueError):
                normalizeSizeRange(faultyValue)

    def test_normalizeSmufl(self):
        with self.assertRaises(TypeError):
            normalizeSmufl(self.font)

    def test_normalizeSmuflName(self):
        with self.assertRaises(TypeError):
            normalizeSmuflName(0)
        for name in self.faultyNames:
            with self.assertRaises(ValueError):
                normalizeSmuflName(name)

    def test_normalizeEngravingDefaults(self):
        with self.assertRaises(TypeError):
            normalizeEngravingDefaults(self.font)

    def test_normalizeEngravingDefaultsAttr(self):
        for wrongAttr, wrongVal in [('attribute', '23'),
                                    ('attribute', [23]),
                                    ('textFontFamily', [23])]:
            with self.assertRaises(TypeError):
                normalizeEngravingDefaultsAttr(wrongAttr, wrongVal)
        with self.assertRaises(ValueError):
            normalizeEngravingDefaultsAttr('textFontFamily', [''])

    def test_normalizeRequest(self):
        with self.assertRaises(TypeError):
            normalizeEngravingDefaults('path')

    def test_normalizeRequestPath(self):
        with self.assertRaises(TypeError):
            normalizeEngravingDefaults(['path'])


if __name__ == '__main__':
    unittest.main()
