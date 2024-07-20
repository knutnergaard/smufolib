import unittest
import random
from pathlib import Path
from smufolib import Font, Glyph, Range, converters
from bin.importID import importID

# pylint: disable=C0115, C0116, C0103


class TestRange(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Populate font with glyphs of different ranges and save to cwd.
        # cls.font = Font()
        # population = range(0xE000, 0xF3FF)
        # for number in random.choices(population, k=20):
        #     glyphName = converters.toUniName(number)
        #     cls.font[glyphName] = Glyph()
        #     cls.font[glyphName].unicode = number
        # cls.font.save('./testRangeFont.ufo')

        # Add SMuFl names to glyphs.
        importID(cls.font, 'name')

    def test_smufl(self):
        pass

    def test_glyph(self):
        pass

    def test_font(self):
        pass

    def test_layer(self):
        pass

    def test_name(self):
        pass

    def test_description(self):
        pass

    def test_glyphs(self):
        pass

    def test_start(self):
        pass

    def test_end(self):
        pass


if __name__ == '__main__':
    unittest.main()
