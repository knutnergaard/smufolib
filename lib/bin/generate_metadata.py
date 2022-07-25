#!/usr/bin/env python3
"""
SMuFL metadata generator.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from smufolib import config, structures, validators
from smufolib.font import Font

CONFIG = config.configLoad()

# pylint: disable=too-many-ancestors, invalid-name


def generateMetadata(font: Font = Font(),
                     filepath: str | Path =
                     CONFIG['fontPaths']['metadataJson']):
    """
    Generates metadata as JSON and saves.

    All keys are sorted alphabetically for the time being, even though
    bravura_metadata.json has fontName and fontVersion as prelimenary
    keys, while all others are sorted.

    If filepath is None, output file is saved in the font's directory.
    By default, specified path and name in config is used.
    """
    # Facilitate command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', default=font)
    parser.add_argument('--filepath', default=filepath)
    args = parser.parse_args()

    if not args.filepath:
        args.filepath = config.setDefaultPath(args.font, 'metadata.json')
    metadata = _compileMetadata(args.font)
    print(f'Writing metadata to: {args.filepath}')

    with open(args.filepath, 'w', encoding='utf-8') as outfile:
        json.dump(metadata, outfile, indent=4, sort_keys=True)

    print('All done!')


def _compileMetadata(font):
    # Builds SMuFL-specific metadata dictionary.
    print('Building metadata ...')

    template = structures.TEMPLATE

    # fontName, fontVersion, engravingDefaults
    template['fontName'] = font.name
    template['fontVersion'] = font.version
    template['engravingDefaults'] = font.engravingDefaults

    sets, setglyphs = {}, []

    for glyph in font:
        if not validators.validateGlyph(glyph):
            continue

        name = glyph.smuflName

        # glyphAdvanceWidths, glyphBBoxes
        template['glyphAdvanceWidths'][name] = glyph.advanceWidth
        template['glyphBBoxes'][name] = glyph.bBox

        # glyphsWithAlternates
        if glyph.alternates:
            baseglyphs = {}
            baseglyphs['alternates'] = glyph.alternates
            template['glyphsWithAlternates'][name] = baseglyphs

        # glyphsWithAnchors
        if glyph.anchors:
            template['glyphsWithAnchors'][name] = glyph.anchors

        # ligatures
        if glyph.isLigature:
            template['ligatures'][name] = {}
            template['ligatures'][name]["codepoint"] = glyph.codepoint
            if glyph.components:
                template['ligatures'][name]['componentGlyphs'] = glyph.components
            template['ligatures'][name]["description"] = glyph.description

        # optionalGlyphs
        if glyph.isOptional:
            template['optionalGlyphs'][name] = {}
            template['optionalGlyphs'][name]['codepoint'] = glyph.codepoint
            template['optionalGlyphs'][name]['description'] = glyph.description
            template['optionalGlyphs'][name]['classes'] = glyph.classes

        # sets
        if glyph.isSet:
            sets[glyph.suffix] = structures.SETS[glyph.suffix]
            glyphinfo = {"alternateFor": glyph.base.smuflName,
                         "codepoint": glyph.codepoint,
                         "description": glyph.description,
                         "name": glyph.smuflName}
            setglyphs.append(glyphinfo)
            template['sets'] = sets
            template['sets'][glyph.suffix]['glyphs'] = setglyphs

    return template


if __name__ == '__main__':
    generateMetadata()
