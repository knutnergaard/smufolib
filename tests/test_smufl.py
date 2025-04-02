import unittest
from unittest.mock import patch, PropertyMock
from smufolib import converters, Smufl


class TestSmufl(unittest.TestCase):
    def setUp(self):
        # Create generic objects
        # pylint: disable=E1101
        self.font, _ = self.objectGenerator("font")
        self.other_font, _ = self.objectGenerator("font")
        self.smufl, _ = self.objectGenerator("smufl")
        self.engravingDefaults, _ = self.objectGenerator("engravingDefaults")
        self.glyph, _ = self.objectGenerator("glyph")
        self.other_glyph, _ = self.objectGenerator("glyph")
        self.range, _ = self.objectGenerator("range")

        # pylint: enable=E1101
        # Create layer and assign to font
        self.layer = self.font.newLayer("testLayer")
        self.font.defaultLayer = self.layer

        # Generate different types of glyphs to layer
        self.recommended1, self.recommended2 = self.generate_recommended_glyphs()
        self.ligature = self.generate_ligature()
        self.ligature_components = self.generate_ligature_components(self.ligature)
        self.optional = self.generate_optional()
        self.salt = self.generate_salt()
        self.set = self.generate_set()
        self.non_member1, self.non_member2 = self.generate_non_member_glyphs()

    # -------
    # Helpers
    # -------

    def generate_recommended_glyphs(self):
        glyph1 = self.layer.newGlyph("uniE000")
        glyph1.unicode = 0xE000
        glyph2 = self.layer.newGlyph("uniF3FF")
        glyph2.unicode = 0xF3FF
        return glyph1, glyph2

    def generate_ligature(self):
        glyph = self.layer.newGlyph("uniE000_uniE001_uniE002")
        glyph.unicode = 0xF400
        return glyph

    def generate_ligature_components(self, ligature):
        glyphs = []
        for i, component_name in enumerate(ligature.name.split("_")):
            glyph = self.layer.newGlyph(component_name)
            glyph.unicode = converters.toDecimal(component_name)
            glyph.lib["com.smufolib.name"] = f"smuflName{i}"
            glyphs.append(glyph)
        return tuple(glyphs)

    def generate_optional(self):
        glyph = self.layer.newGlyph("optionalGlyph")
        glyph.unicode = 0xF400
        return glyph

    def generate_salt(self):
        glyph = self.layer.newGlyph("uniE000.salt01")
        glyph.unicode = 0xF8FF
        return glyph

    def generate_set(self):
        glyph = self.layer.newGlyph("uniE000.ss01")
        glyph.unicode = 0xF400
        return glyph

    def generate_non_member_glyphs(self):
        glyph1 = self.layer.newGlyph("nonSmuflGlyph1")
        glyph1.unicode = 0xE000 - 1
        glyph2 = self.layer.newGlyph("nonSmuflGlyph2")
        glyph2.unicode = 0xF8FF + 1
        return glyph1, glyph2

    def set_dimensionsions(self, glyph, width, height):
        glyph.width = width
        glyph.height = height
        return glyph

    def draw_paths(self, glyph):
        pen = glyph.getPen()
        pen.moveTo((100, -10))
        pen.lineTo((100, 100))
        pen.lineTo((200, 100))
        pen.lineTo((200, 0))
        pen.closePath()
        pen.moveTo((110, 10))
        pen.lineTo((110, 90))
        pen.lineTo((190, 90))
        pen.lineTo((190, 10))
        pen.closePath()

    def assign_anchors(self, glyph):
        glyph.appendAnchor("stemUpNW", (1.5, 2.5))
        glyph.appendAnchor("nonSmuflAnchor", (3.5, 4.5))

    def set_spaces(self, font):
        font.info.unitsPerEm = 1000
        font.lib["com.smufolib.spaces"] = True
        return font

    # ----
    # repr
    # ----

    # pylint: disable=W0212
    def test_reprContents_with_font(self):
        self.smufl.font = self.font
        value = self.smufl._reprContents()
        self.assertIsInstance(value, list)
        for i in value:
            self.assertIsInstance(i, str)

    def test_reprContents_with_glyph(self):
        self.smufl.glyph = self.glyph
        value = self.smufl._reprContents()
        self.assertIn("in glyph", value)
        self.assertIn(self.glyph._reprContents()[0], value)

    # pylint: enable=W0212

    # -------
    # Parents
    # -------

    def test_get_glyph(self):
        self.smufl.glyph = self.glyph
        self.assertIsNotNone(self.smufl.glyph)
        self.assertIs(self.smufl.glyph, self.glyph)

    def test_set_glyph_with_preset_font(self):
        self.smufl.font = self.font
        with self.assertRaises(AssertionError):
            self.smufl.glyph = self.glyph

    def test_set_glyph_with_same_preset_glyph(self):
        self.smufl.glyph = self.glyph
        with self.assertRaises(AssertionError):
            self.smufl.glyph = self.other_glyph

    def test_parent_no_glyph(self):
        self.assertIsNone(self.smufl.font)
        self.assertIsNone(self.smufl.layer)
        self.assertIsNone(self.smufl.glyph)

    def test_get_font(self):
        self.smufl.font = self.font
        self.assertIsNotNone(self.smufl.font)
        self.assertIs(self.smufl.font, self.font)

    def test_get_no_font(self):
        self.smufl.glyph = self.glyph
        self.assertIsNone(self.smufl.font)

    def test_set_font_with_same_preset_font(self):
        self.smufl.font = self.font
        with self.assertRaises(AssertionError):
            self.smufl.font = self.other_font

    def test_set_font_with_preset_glyph(self):
        self.smufl.glyph = self.glyph
        with self.assertRaises(AssertionError):
            self.smufl.font = self.font

    # -------------
    # Font Metadata
    # -------------

    def test_get_designSize(self):
        self.smufl.font = self.font
        self.font.lib["com.smufolib.designSize"] = 1000
        self.assertEqual(self.smufl.designSize, 1000)

    def test_set_designSize(self):
        self.smufl.font = self.font
        self.smufl.designSize = 1000
        self.assertEqual(self.smufl.designSize, 1000)

    def test_designSize_removal(self):
        self.smufl.font = self.font
        self.font.lib["com.smufolib.designSize"] = 1000
        self.smufl.designSize = None
        self.assertIsNone(self.smufl.designSize)
        self.assertNotIn("com.smufolib.desgnSize", self.font.lib)

    def test_get_engravingDefaults(self):
        self.smufl.font = self.font
        self.assertIsInstance(
            self.smufl.engravingDefaults, type(self.engravingDefaults)
        )

    def test_set_engravingDefaults(self):
        self.other_font.smufl.engravingDefaults.stemThickness = 10
        self.font.smufl.engravingDefaults = self.other_font.smufl.engravingDefaults
        self.assertEqual(self.font.smufl.engravingDefaults.stemThickness, 10)

    def test_get_sizeRange(self):
        self.smufl.font = self.font
        self.font.lib["com.smufolib.sizeRange"] = (10, 36)
        self.assertEqual(self.smufl.sizeRange, (10, 36))

    def test_get_sizeRange_no_font(self):
        self.assertIsNone(self.smufl.sizeRange)

    def test_set_sizeRange(self):
        self.smufl.font = self.font
        self.smufl.sizeRange = (10, 36)
        self.assertEqual(self.smufl.sizeRange, (10, 36))

    def test_sizeRange_removal(self):
        self.smufl.font = self.font
        self.font.lib["com.smufolib.sizeRange"] = (10, 36)
        self.smufl.sizeRange = None
        self.assertEqual(self.smufl.sizeRange, None)
        self.assertNotIn("com.smufolib.sizeRange", self.font.lib)

    # --------------
    # Glyph metadata
    # --------------

    def test_alternates(self):
        self.assertIsNone(self.smufl.alternates)
        self.assertEqual(self.optional.smufl.alternates, ())
        self.assertEqual(
            self.recommended1.smufl.alternates,
            (
                {"codepoint": "U+F8FF", "name": None},
                {"codepoint": "U+F400", "name": None},
            ),
        )

    def test_anchors(self):
        self.assertIsNone(self.smufl.anchors)
        self.assign_anchors(self.glyph)
        self.smufl.glyph = self.glyph
        self.assertEqual(self.smufl.anchors, {"stemUpNW": (1.5, 2.5)})

    @patch.object(Smufl, "spaces", new_callable=PropertyMock, return_value=True)
    def test_anchors_with_toSpaces_None(self, mock_spaces):
        self.smufl.glyph = self.glyph
        self.assign_anchors(self.glyph)
        self.assertIsNone(self.glyph.smufl.anchors)

    def test_bBox(self):
        self.assertIsNone(self.smufl.bBox)
        self.draw_paths(self.glyph)
        self.smufl.glyph = self.glyph
        self.assertEqual(self.smufl.bBox, {"bBoxSW": (100, -10), "bBoxNE": (200, 100)})

    def test_bBox_with_spaces(self):
        self.draw_paths(self.recommended1)
        self.assign_anchors(self.glyph)
        self.set_spaces(self.font)
        self.assertEqual(
            self.recommended1.smufl.bBox,
            {"bBoxSW": (100 / 250, -10 / 250), "bBoxNE": (200 / 250, 100 / 250)},
        )

    def test_get_codepoint(self):
        self.smufl.glyph = self.glyph
        self.assertIsNone(self.smufl.codepoint)
        self.glyph.unicode = 0xE111
        self.assertEqual(self.smufl.codepoint, "U+E111")

    def test_set_codepoint(self):
        self.smufl.glyph = self.glyph
        self.smufl.codepoint = "U+E111"
        self.assertEqual(self.smufl.codepoint, "U+E111")
        self.smufl.codepoint = None
        self.assertIsNone(self.glyph.unicode)

    def test_componentGlyphs(self):
        self.assertEqual(self.ligature.smufl.componentGlyphs, self.ligature_components)
        self.assertIsNone(self.smufl.componentGlyphs)
        self.assertEqual(self.recommended1.smufl.componentGlyphs, ())

    def test_componentNames(self):
        componentNames = tuple(glyph.smufl.name for glyph in self.ligature_components)
        self.assertEqual(self.ligature.smufl.componentNames, componentNames)
        self.assertIsNone(self.smufl.componentNames)
        self.assertEqual(self.recommended1.smufl.componentNames, ())

    def test_range(self):
        self.assertIsInstance(self.recommended1.smufl.range, type(self.range))

    def test_get_advanceWidth(self):
        self.assertIsNone(self.smufl.advanceWidth)
        self.smufl.glyph = self.glyph
        self.glyph.width = 500
        self.assertEqual(self.smufl.advanceWidth, 500)

    def test_set_advanceWidth(self):
        self.smufl.glyph = self.glyph
        self.glyph.smufl.advanceWidth = 500
        self.assertEqual(self.smufl.advanceWidth, 500)

    def test_set_advanceWidth_with_spaces(self):
        self.set_spaces(self.font)
        self.recommended1.smufl.advanceWidth = 2
        self.font.lib.pop("com.smufolib.spaces")
        self.assertEqual(self.recommended1.smufl.advanceWidth, 500)

    # --------------
    # Identification
    # --------------

    def test_get_version(self):
        self.assertIsNone(self.smufl.version)
        self.smufl.font = self.font
        self.font.info.versionMajor = 1
        self.font.info.versionMinor = 0
        self.assertEqual(self.smufl.version, 1.0)

    def test_set_version(self):
        self.smufl.font = self.font
        self.smufl.version = 1.0
        self.assertEqual(self.smufl.version, 1.0)
        self.smufl.version = None
        self.assertIsNone(self.font.info.versionMinor)
        self.assertIsNone(self.font.info.versionMajor)

    def test_get_classes(self):
        self.smufl.glyph = self.glyph
        self.glyph.lib["com.smufolib.classes"] = ["class1", "class2"]
        self.assertEqual(self.smufl.classes, ("class1", "class2"))

    def test_get_classes_no_font(self):
        self.assertIsNone(self.smufl.classes)

    def test_set_classes(self):
        self.smufl.glyph = self.glyph
        self.smufl.classes = ["class1", "class2"]
        self.assertEqual(self.smufl.classes, ("class1", "class2"))

    def test_classes_removal(self):
        self.smufl.glyph = self.glyph
        self.glyph.lib["com.smufolib.classes"] = ["class1", "class2"]
        self.smufl.classes = None
        self.assertEqual(self.smufl.classes, ())
        self.assertNotIn("com.smufolib.classes", self.glyph.lib)

    def test_get_description(self):
        self.assertIsNone(self.smufl.description)
        self.smufl.glyph = self.glyph
        self.glyph.lib["com.smufolib.description"] = "Test description"
        self.assertEqual(self.smufl.description, "Test description")

    def test_set_description(self):
        self.smufl.glyph = self.glyph
        self.smufl.description = "Test description"
        self.assertEqual(self.smufl.description, "Test description")

    def test_description_removal(self):
        self.smufl.glyph = self.glyph
        self.glyph.lib["com.smufolib.description"] = "Test description"
        self.smufl.description = None
        self.assertIsNone(self.smufl.designSize)
        self.assertNotIn("com.smufolib.desgnSize", self.glyph.lib)

    def test_get_name_with_font(self):
        self.assertIsNone(self.smufl.name)
        self.smufl.font = self.font
        self.font.info.familyName = "testName"
        self.assertEqual(self.smufl.name, "testName")

    def test_set_name_with_font(self):
        self.smufl.font = self.font
        self.smufl.name = "testName"
        self.assertEqual(self.smufl.name, "testName")

    def test_set_name_without_font(self):
        self.smufl.name = "testName"
        self.assertIsNone(self.smufl.name)
        self.assertIsNone(self.smufl._names)

    def test_get_name_with_glyph(self):
        self.recommended1.lib["com.smufolib.name"] = "testName"
        self.assertEqual(self.recommended1.smufl.name, "testName")

    def test_set_name_with_glyph(self):
        self.recommended1.smufl.name = "testName1"
        self.assertEqual(self.recommended1.smufl.name, "testName1")
        self.assertEqual(
            self.recommended1.font.lib["com.smufolib.names"], {"testName1": "uniE000"}
        )

        self.recommended2.smufl.name = "testName2"
        self.assertIn("testName2", self.font.lib["com.smufolib.names"])

        self.recommended1.smufl.name = None
        self.assertNotIn("testName1", self.font.lib["com.smufolib.names"])

        self.recommended2.smufl.name = None
        self.assertNotIn("com.smufolib.names", self.font.lib)

    # ----------
    # Validation
    # ----------

    def test_isLigature(self):
        self.assertTrue(self.ligature.smufl.isLigature)
        self.assertFalse(self.recommended1.smufl.isLigature)

    def test_isMember(self):
        self.assertTrue(self.recommended1.smufl.isMember)
        self.assertTrue(self.recommended2.smufl.isMember)
        self.assertFalse(self.non_member1.smufl.isMember)
        self.assertFalse(self.non_member2.smufl.isMember)

    def test_isOptional(self):
        self.assertTrue(self.optional.smufl.isOptional)
        self.assertFalse(self.recommended1.smufl.isOptional)

    def test_isRecommended(self):
        self.assertTrue(self.recommended1.smufl.isRecommended)
        self.assertTrue(self.recommended2.smufl.isRecommended)
        self.assertFalse(self.optional.smufl.isRecommended)

    def test_isSalt(self):
        self.assertTrue(self.salt.smufl.isSalt)
        self.assertFalse(self.set.smufl.isSalt)

    def test_isSet(self):
        self.assertTrue(self.set.smufl.isSet)
        self.assertFalse(self.salt.smufl.isSet)

    # -----------------------------
    # Normalization and Measurement
    # -----------------------------

    def test_round(self):
        self.set_dimensionsions(self.recommended1, 100.5, 100.5)
        self.assign_anchors(self.recommended1)
        self.set_spaces(self.font)
        self.recommended1.smufl.round()
        self.assertEqual(self.recommended1.smufl.advanceWidth, 100.5 / 250)
        self.assertEqual(
            self.recommended1.smufl.anchors, {"stemUpNW": (1.5 / 250, 2.5 / 250)}
        )

        self.recommended1.font.lib.pop("com.smufolib.spaces")
        self.recommended1.smufl.round()
        self.assertEqual(self.recommended1.smufl.advanceWidth, 101)
        self.assertEqual(self.recommended1.smufl.anchors, {"stemUpNW": (2, 3)})

    def test_toSpaces(self):
        self.assertIsNone(self.glyph.smufl.toSpaces(0.5))
        self.recommended1.font.info.unitsPerEm = 1000
        self.assertEqual(self.recommended1.smufl.toSpaces(125), 0.5)

    def test_toUnits(self):
        self.assertIsNone(self.glyph.smufl.toUnits(0.5))
        self.recommended1.font.info.unitsPerEm = 1000
        self.assertEqual(self.recommended1.smufl.toUnits(0.499), 125)
        self.assertEqual(self.recommended1.smufl.toUnits(0.499, rounded=False), 124.75)

    def test_spaces(self):
        self.assertFalse(self.recommended1.smufl.spaces)
        with self.assertRaises(AttributeError):
            self.recommended1.smufl.spaces = True
        self.recommended1.font.info.unitsPerEm = 1000
        self.recommended1.smufl.spaces = True
        self.assertTrue(self.recommended1.smufl.spaces)
        self.recommended1.smufl.spaces = False
        self.assertNotIn("com.smufolib.spaces", self.font.lib)

    # -----
    # Other
    # -----

    def test_base(self):
        self.assertEqual(self.salt.smufl.base.name, self.recommended1.name)
        self.assertEqual(self.recommended1.smufl.base.name, self.recommended1.name)

    def test_base_no_font(self):
        self.smufl.glyph = self.glyph
        self.glyph.name = "uniE000.salt"
        self.assertIsNone(self.glyph.smufl.base)

    def test_base_no_glyph_name(self):
        self.smufl.glyph = self.glyph
        self.assertIsNone(self.glyph.smufl.base)

    def test_base_not_in_font(self):
        glyph = self.recommended1
        glyph.font.removeGlyph(self.recommended1.name)
        self.assertIsNone(glyph.smufl.base)

    def test_findGlyph(self):
        self.assertIsNone(self.font.smufl.findGlyph(None))
        self.recommended1.smufl.name = "smuflName1"
        self.assertIsInstance(self.font.smufl.findGlyph("smuflName1"), type(self.glyph))
        self.assertIsNone(self.font.smufl.findGlyph("smuflName2"))

    def test_suffix(self):
        self.assertEqual(self.salt.smufl.suffix, "salt01")
        self.assertIsNone(self.recommended1.smufl.suffix)
