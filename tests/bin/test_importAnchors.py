import json
import sys
import unittest
from unittest.mock import patch


from smufolib import Request
from tests.testUtils import (
    SavedFontMixin,
    SavedMetadataMixin,
    SuppressOutputMixin,
    generateGlyph,
    getVerboseOutput,
)
from bin.importAnchors import importAnchors, main


class TestGenerateMetadataScript(
    SavedFontMixin, SavedMetadataMixin, SuppressOutputMixin, unittest.TestCase
):
    def setUp(self):
        super().setUp()
        # fmt: off
        self.metadata = {
            "glyphsWithAnchors": {
                "testGlyph1": {
                    "stemUpNW": [1.0, 1.0]
                    }
            
            }
        }
        # fmt: on
        self.saveMetadataToTemp()

        self.font, _ = self.objectGenerator("font")  # pylint: disable=E1101
        self.font.smufl.name = "testFont"
        self.font.info.unitsPerEm = 1000
        self.glyph = generateGlyph(
            self.font,
            "testGlyph1",
            smuflName="testGlyph1",
            anchors=[
                (
                    "nonSmuflAnchor",
                    (0, 0),
                )
            ],
        )
        generateGlyph(self.font, "nonSmuflGlyph")
        self.anchorName = "stemUpNW"
        self.colorDict = {self.anchorName: (1, 0, 0, 1)}

        self.saveFontToTemp()
        self.suppressOutput()

    def test_importAnchors_basic(self):
        importAnchors(self.font, fontData=self.metadataPath)
        anchors = self.metadata["glyphsWithAnchors"]["testGlyph1"]
        result = {
            k: tuple(self.font.smufl.toUnits(n) for n in v) for k, v in anchors.items()
        }
        self.assertEqual(self.glyph.smufl.anchors, result)
        anchorNames = [a.name for a in self.glyph.anchors]
        self.assertIn("nonSmuflAnchor", anchorNames)

    def test_importAnchors_verbose(self):
        output = getVerboseOutput(
            importAnchors,
            font=self.font,
            fontData=self.metadataPath,
            verbose=True,
        )
        self.assertIn("\nCompiling glyph data...", output)
        self.assertIn(
            f"\nAppending anchors to glyph '{self.glyph.smufl.name}':", output
        )
        for anchor in self.glyph.anchors:
            name = anchor.name
            if name != "nonSmuflAnchor":
                self.assertIn(f"\t{name}", output)

    def test_importAnchors_missing_smufl_names(self):
        self.glyph.smufl.name = None
        with self.assertRaises(ValueError):
            importAnchors(self.font, fontData=self.metadataPath)

    def test_importAnchors_clear_anchors(self):
        importAnchors(self.font, fontData=self.metadataPath, clear=True)
        anchorNames = [a.name for a in self.glyph.anchors]
        self.assertNotIn("nonSmuflAnchor", anchorNames)

    def test_importAnchors_mark(self):
        importAnchors(
            self.font, fontData=self.metadataPath, mark=True, colors=self.colorDict
        )
        [result] = [a.color for a in self.glyph.anchors if a.name == self.anchorName]
        self.assertEqual(self.colorDict[self.anchorName], result)

    @patch("bin.importAnchors.importAnchors")
    def test_main(self, mock_generateMetadata):
        colorsJson = json.dumps(self.colorDict)

        test_args = [
            "importAnchors",
            str(self.fontPath),
            "--font-data",
            str(self.metadataPath),
            "--mark",
            "--colors",
            colorsJson,
            "--clear",
            "--verbose",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        mock_generateMetadata.assert_called_once()
        args, kwargs = mock_generateMetadata.call_args
        self.assertIsInstance(args[0], type(self.font))
        self.assertIsInstance(kwargs["fontData"], Request)
        self.assertTrue(kwargs["mark"])
        self.assertEqual(kwargs["colors"].keys(), self.colorDict.keys())
        self.assertCountEqual(kwargs["colors"], self.colorDict)
        self.assertTrue(kwargs["clear"])
        self.assertTrue(kwargs["verbose"])
