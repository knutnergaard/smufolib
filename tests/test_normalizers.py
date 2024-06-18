import unittest
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
    def getFont_layers(self):
        font, _ = self.objectGenerator("font")
        for name in ["A", "B", "C", "D", "E"]:
            font.newLayer(name)
        return font

    def test_normalizeFont(self):
        self.assertEqual(normalizeFont(getFont_layers()), getFont_layers())

    def test_normalizeClasses(self):
        pass

    def test_normalizeDescription(self):
        pass

    def test_normalizeDesignSize(self):
        pass

    def test_normalizeSizeRange(self):
        pass

    def test_normalizeSmufl(self):
        pass

    def test_normalizeSmuflName(self):
        pass

    def test_normalizeEngravingDefaults(self):
        pass

    def test_normalizeEngravingDefaultsAttr(self):
        pass

    def test_normalizeRequest(self):
        pass

    def test_normalizeRequestPath(self):
        pass


if __name__ == '__main__':
    unittest.main()
