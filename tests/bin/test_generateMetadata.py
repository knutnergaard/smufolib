import json
import sys
import unittest
from unittest.mock import patch


import smufolib
from tests.testUtils import (
    SavedFontMixin,
    SavedMetadataMixin,
    SuppressOutputMixin,
    generateGlyph,
)
from bin.generateMetadata import generateMetadata, main, _compileMetadata


class TestGenerateMetadata(
    SavedFontMixin, SavedMetadataMixin, SuppressOutputMixin, unittest.TestCase
):
    def setUp(self):
        super().setUp()
        self.suppressOutput()
        smufolib.objects.smufl.STRICT_CLASSES = False
        # fmt: off
        self.metadata = {
            "fontName": "testFont",
            "fontVersion": 1.0,
            "designSize": 20,
            "sizeRange": [16, 24],
            "engravingDefaults":{
		"arrowShaftThickness": None,
		"barlineSeparation": None,
		"beamSpacing": None,
		"beamThickness": None,
		"bracketThickness": None,
		"dashedBarlineDashLength": None,
		"dashedBarlineGapLength": None,
		"dashedBarlineThickness": None,
		"hBarThickness": None,
		"hairpinThickness": None,
		"legerLineExtension": None,
		"legerLineThickness": None,
		"lyricLineThickness": None,
		"octaveLineThickness": None,
		"pedalLineThickness": None,
		"repeatBarlineDotSeparation": None,
		"repeatEndingLineThickness": None,
		"slurEndpointThickness": None,
		"slurMidpointThickness": None,
		"staffLineThickness": 0.5, 
		"stemThickness": 0.5,
		"subBracketThickness": None,
		"textEnclosureThickness": None,
		"textFontFamily":[],
		"thickBarlineThickness": None,
		"thinBarlineThickness": None,
        "thinThickBarlineSeparation": None,
		"tieEndpointThickness": None,
		"tieMidpointThickness": None,
		"tupletBracketThickness": None
	},
            "glyphAdvanceWidths": {
                "testGlyph1": 2.0,
                "testGlyph2": 2.0,
                "testAlternate": 2.0,
                "testLigature": 2.0
                },
            "glyphBBoxes": {
                "testGlyph1": {
                    "bBoxNE": [2.0, 2.0],
                    "bBoxSW": [0.0, 0.0]
                },
                "testGlyph2": {
                    "bBoxNE": [2.0, 2.0],
                    "bBoxSW": [0.0, 0.0]
                },
                "testAlternate": {
                    "bBoxNE": [2.0, 2.0],
                    "bBoxSW": [0.0, 0.0]
                },
                "testLigature": {
                    "bBoxNE": [2.0, 2.0],
                    "bBoxSW": [0.0, 0.0]
                }
            },
            "glyphsWithAlternates": {
                "testGlyph1": {
                    "alternates": [
                        {
                        "codepoint": "U+F401", 
                        "name": "testAlternate"
                        }
                    ]
                }
            },
            "glyphsWithAnchors": {
                "testGlyph1": {
                    "stemUpNW": [1.0, 1.0]
                    }
            },
            "ligatures": {
                "testLigature": {
                    "codepoint": "U+F402",
                    "componentGlyphs": [
                        "testGlyph1",
                        "testGlyph2"
                    ],
                    "description": "Ligature of testGlyph1 and testGlyph2"
                }
            },
            "optionalGlyphs": {
                "testLigature": {
                    "classes": ["testClass"],
                    "codepoint": "U+F402",
                    "description": "Ligature of testGlyph1 and testGlyph2"
                },
                "testAlternate": {
                    "classes": ["testClass"],
                    "codepoint": "U+F401",
                    "description": "Alternate for testGlyph1"
                }
            },
            "sets": {
                "ss01": {
                    "description": "Test stylistic set",
                    "glyphs": [
                        {
                            "alternateFor": "testGlyph1",
                            "codepoint": "U+F401",
                            "description": "Alternate for testGlyph1",
                            "name": "testAlternate"
                        }
                    ],
                    "type": "alternate"
                }
            }
        }
        # fmt: on
        self.metadataPath = self.saveMetadataToTemp()

        self.font, _ = self.objectGenerator("font")  # pylint: disable=E1101
        self.font.info.unitsPerEm = 1000
        self.font.smufl.name = self.metadata["fontName"]
        self.font.smufl.version = self.metadata["fontVersion"]
        self.font.smufl.spaces = True
        self.font.smufl.designSize = self.metadata["designSize"]
        self.font.smufl.sizeRange = self.metadata["sizeRange"]
        self.font.smufl.engravingDefaults.update(self.metadata["engravingDefaults"])

        generateGlyph(
            self.font,
            "uniE001",
            unicode=0xE001,
            smuflName="testGlyph1",
            anchors=[("stemUpNW", (250, 250))],
            width=500,
            description="Test glyph 1",
            classes=["testClass"],
            points=((0, 0), (500, 0), (500, 500), (0, 500)),
        )
        generateGlyph(
            self.font,
            "uniE002",
            unicode=0xE002,
            smuflName="testGlyph2",
            width=500,
            description="Test glyph 2",
            classes=["testClass"],
            points=((0, 0), (500, 0), (500, 500), (0, 500)),
        )
        generateGlyph(
            self.font,
            "uniE001.ss01",
            unicode=0xF401,
            smuflName="testAlternate",
            width=500,
            description="Alternate for testGlyph1",
            classes=["testClass"],
            points=((0, 0), (500, 0), (500, 500), (0, 500)),
        )
        generateGlyph(
            self.font,
            "uniE001_uniE002",
            unicode=0xF402,
            smuflName="testLigature",
            width=500,
            description="Ligature of testGlyph1 and testGlyph2",
            classes=["testClass"],
            points=((0, 0), (500, 0), (500, 500), (0, 500)),
        )
        self.fontPath = self.saveFontToTemp()

    def test_generate_metadata(self):
        generateMetadata(
            self.font, self.tempPath, fontData=self.metadataPath, verbose=False
        )

        json_path = self.tempPath / "testFont.json"
        self.assertTrue(json_path.exists())

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertDictEqual(data, self.metadata)

    @patch("bin.generateMetadata.generateMetadata")
    def test_main(self, mock_generateMetadata):
        test_args = [
            "generateMetadata",
            str(self.fontPath),
            str(self.tempPath),
            "--font-data",
            str(self.metadataPath),
            "--verbose",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        mock_generateMetadata.assert_called_once()
        args, kwargs = mock_generateMetadata.call_args
        self.assertIsInstance(args[0], type(self.font))
        self.assertEqual(args[1], str(self.tempPath))
        self.assertIsInstance(kwargs["fontData"], smufolib.Request)
        self.assertTrue(kwargs["verbose"])

    def test_compileMetadata_no_font_attribute_value(self):
        self.font.smufl.version = None
        result = _compileMetadata(self.font, self.metadata, verbose=False)
        self.assertNotIn("fontVersion", result)

    def test_compileMetadata_no_glyph_attribute_value(self):
        glyph = self.font["uniE001"]
        glyph.unicode = None
        result = _compileMetadata(self.font, self.metadata, verbose=False)
        self.assertNotIn("testGlyph1", result["glyphAdvanceWidths"])
