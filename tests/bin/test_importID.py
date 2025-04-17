"""importID(
font: Font | Path | str,
attributes: str | tuple[str, ...] = "*",
classesData: Request | Path | str = CLASSES_DATA,
glyphnamesData: Request | Path | str = GLYPHNAMES_DATA,
fontData: Request | Path | str = FONT_DATA,
includeOptionals: bool = INCLUDE_OPTIONALS,
overwrite: bool = OVERWRITE,
verbose: bool = VERBOSE,"""

import sys
import unittest
from unittest.mock import patch

from smufolib import Request
from smufolib.utils import converters
from tests.testUtils import (
    SavedFontMixin,
    SavedMetadataMixin,
    SuppressOutputMixin,
    generateGlyph,
    getVerboseOutput,
)
from bin.importID import ATTRIBUTES, importID, main


class TestImportID(
    SavedFontMixin, SavedMetadataMixin, SuppressOutputMixin, unittest.TestCase
):
    def setUp(self):
        super().setUp()
        self.suppressOutput()

        self.font, _ = self.objectGenerator("font")  # pylint: disable=E1101
        self.fontPath = self.saveFontToTemp()
        self.classesData = {
            "accidentals": ["accidentalFlat"],
            "accidentalsSagittalMixed": ["accidentalFlat"],
        }
        self.glyphnamesData = {
            "accidentalFlat": {
                "alternateCodepoint": "U+266D",
                "codepoint": "U+E260",
                "description": "Flat",
            },
        }
        self.fontData = {
            "ligatures": {
                "accidentalFlatParens": {
                    "codepoint": "U+F5E0",
                    "description": "Parenthesised flat",
                },
            },
            "optionalGlyphs": {
                "accidentalFlatSmall": {
                    "classes": [
                        "accidentals",
                        "accidentalsSagittalMixed",
                        "accidentalsStandard",
                        "combiningStaffPositions",
                    ],
                    "codepoint": "U+F427",
                    "description": "Flat (for small staves)",
                },
                "accidentalFlatParens": {
                    "classes": ["testGlyph"],
                    "codepoint": "U+F5E0",
                },
            },
        }
        self.classesDataPath = self.saveMetadataToTemp(
            self.classesData, "classesData.json"
        )
        self.glyphnamesDataPath = self.saveMetadataToTemp(
            self.glyphnamesData, "glyphnamesData.json"
        )
        self.fontDataPath = self.saveMetadataToTemp(self.fontData, "fontData.json")

        for codepoint in self.extractCodepoints(self.glyphnamesData, self.fontData):
            name = converters.toUniName(codepoint)
            generateGlyph(self.font, name=name, codepoint=codepoint)

    def extractCodepoints(self, *metadataDicts):
        codepoints = []

        def traverseDict(d):
            for key, value in d.items():
                if key == "codepoint":
                    codepoints.append(value)
                elif isinstance(value, dict):
                    traverseDict(value)

        for metadata in metadataDicts:
            if isinstance(metadata, dict):
                traverseDict(metadata)
        return codepoints

    def test_importID_basic(self):
        importID(
            self.font,
            classesData=self.classesDataPath,
            glyphnamesData=self.glyphnamesDataPath,
            fontData=self.fontDataPath,
            includeOptionals=False,
        )
        glyph = self.font["uniE260"]
        for attr in ATTRIBUTES:
            result = getattr(glyph.smufl, attr)
            self.assertTrue(result)

    def test_importID_includeOptionals(self):
        importID(
            self.font,
            classesData=self.classesDataPath,
            glyphnamesData=self.glyphnamesDataPath,
            fontData=self.fontDataPath,
            includeOptionals=True,
        )
        for glyph in self.font:
            for attr in ATTRIBUTES:
                result = getattr(glyph.smufl, attr)
                if attr == "classes" and glyph.name == "uniF5E0":  # ligature
                    self.assertFalse(result)
                else:
                    self.assertTrue(result)

    def test_importID_singleAttribute(self):
        importID(
            self.font,
            attributes="name",
            classesData=self.classesDataPath,
            glyphnamesData=self.glyphnamesDataPath,
            fontData=self.fontDataPath,
            includeOptionals=True,
        )
        for glyph in self.font:
            result = getattr(glyph.smufl, "name")
            self.assertIsNotNone(result)

    def test_importID_attributeList(self):
        attributes = ["name", "description"]
        importID(
            self.font,
            attributes=attributes,
            classesData=self.classesDataPath,
            glyphnamesData=self.glyphnamesDataPath,
            fontData=self.fontDataPath,
            includeOptionals=True,
        )
        for glyph in self.font:
            for attr in attributes:
                result = getattr(glyph.smufl, attr)
                self.assertIsNotNone(result)

    def test_importID_invalidAttribute(self):
        with self.assertRaises(ValueError):
            importID(
                self.font,
                attributes="invalidAttribute",
                classesData=self.classesDataPath,
                glyphnamesData=self.glyphnamesDataPath,
                fontData=self.fontDataPath,
            )

    def test_importID_overwrite(self):
        nameCounter = 1
        for glyph in self.font:
            glyph.smufl.name = f"testName{nameCounter}"
            nameCounter += 1

        importID(
            self.font,
            attributes="name",
            classesData=self.classesDataPath,
            glyphnamesData=self.glyphnamesDataPath,
            fontData=self.fontDataPath,
            includeOptionals=True,
            overwrite=True,
        )
        for glyph in self.font:
            result = getattr(glyph.smufl, "name")
            self.assertNotIn("testName", result)

    def test_importID_missingCodepoint(self):
        glyph = self.font["uniE260"]
        glyph.unicode = None

        importID(
            self.font,
            attributes="classes",
            classesData=self.classesDataPath,
            glyphnamesData=self.glyphnamesDataPath,
            fontData=self.fontDataPath,
        )
        self.assertFalse(glyph.smufl.classes)

    def test_importID_verbose(self):
        # non-font member
        generateGlyph(self.font, name="nonSmuflGlyph", unicode=ord("a"))
        # non-metadata member
        generateGlyph(self.font, name="uniE000", unicode=0xE000)
        # unencoded member
        generateGlyph(self.font, name="uniE001")
        # preset attribute
        glyph = self.font["uniE260"]
        glyph.smufl.name = "testName"

        output = getVerboseOutput(
            importID,
            self.font,
            classesData=self.classesDataPath,
            glyphnamesData=self.glyphnamesDataPath,
            fontData=self.fontDataPath,
            overwrite=False,
            includeOptionals=True,
            verbose=True,
        )
        self.assertIn("\nBuilding attributesMap...", output)
        self.assertIn("\t'description': not found", output)
        self.assertIn("\t'name': preset", output)
        self.assertIn("\nSkipping non-SMuFL glyph: 'nonSmuflGlyph'", output)
        self.assertIn("\t'name': set", output)
        self.assertIn("\nSaving font...", output)
        for glyph in self.font:
            if glyph.name not in ("nonSmuflGlyph", "uniE001"):
                self.assertIn(f"\nSetting attributes for glyph '{glyph.name}':", output)

    @patch("bin.importID.importID")
    def test_main(self, mock_importID):
        attributes = "*"
        test_args = [
            "importID",
            str(self.fontPath),
            "--attributes",
            attributes,
            "--classes-data",
            str(self.classesDataPath),
            "--glyphnames-data",
            str(self.glyphnamesDataPath),
            "--font-data",
            str(self.fontDataPath),
            "--include-optionals",
            "--overwrite",
            "--verbose",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        mock_importID.assert_called_once()
        args, kwargs = mock_importID.call_args
        self.assertIsInstance(args[0], type(self.font))
        self.assertEqual(args[1], [attributes])
        self.assertIsInstance(kwargs["classesData"], Request)
        self.assertIsInstance(kwargs["glyphnamesData"], Request)
        self.assertIsInstance(kwargs["fontData"], Request)
        self.assertTrue(kwargs["includeOptionals"])
        self.assertTrue(kwargs["overwrite"])
        self.assertTrue(kwargs["verbose"])
