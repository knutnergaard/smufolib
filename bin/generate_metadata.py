#!/usr/bin/env python3
"""SMufoLib Generate Metadata.

This script generates a full featured metadata JSON file for SMuFL fonts
from metadata sources and user specifications. It includes the
follwing sections:

    * mandatory (fontName, fontVersion)
    * size
    * engravingDefaults
    * glyphAdvanceWidths
    * glyphsWithAnchors
    * glyphsWithAlternates
    * glyphBBoxes
    * ligatures
    * sets
    * optionalGlyphs

Sections are automatically added depending on the font's scope and
assigned values.

All keys are sorted alphabetically for the time being, even though
`bravura_metadata.json` shows "fontName" and "fontVersion" as
preliminary keys, while the remaining are sorted alphabetically.

This script requires that `smufolib` be installed within its executive
environment. It may also be imported as a module and contains the
following public functions:

    * `generateMetadata` – main function of the script. See function help
        for parameter details.
"""
from __future__ import annotations
from typing import Any, Dict
import collections
from pathlib import Path
import json

from smufolib import Font, Request, cli, config, validators

CONFIG = config.configLoad()

# pylint: disable=too-many-ancestors, invalid-name


def generateMetadata(font: Font = Font(),
                     target: str | Path =
                     CONFIG['font.paths']['metadataJson']) -> None:
    """Generate metadata JSON file.

    :param font: the script's target font object.
    :param target: filepath to created target JSON file.
    """
    parser = cli.argParser(addHelp=True,
                           description="Generate font metadata JSON file.",
                           font=font, target=target)

    args = parser.parse_args()
    metadata = _compileMetadata(args.font)
    if not args.target:
        args.target = config.setDefaultPath(args.font, 'metadata.json')

    print(f"Writing metadata to: {args.target}")
    with open(args.target, 'w', encoding='utf-8') as outfile:
        json.dump(metadata, outfile, indent=4, sort_keys=False)
    print("Done!")


def _compileMetadata(font) -> Dict[str, Any]:
    # Build SMuFL-specific metadata dictionary.
    print("Compiling metadata...")

    metadata = collections.defaultdict(dict)

    for key in ('fontName', 'fontVersion', 'designSize',
                'sizeRange', 'engravingDefaults'):

        attrName = key[4:].lower() if key.startswith('font') else key
        attribute = getattr(font, attrName)
        if attribute:
            metadata[key] = attribute

    sets, setglyphs = {}, []
    for glyph in font:
        if not validators.validateGlyph(glyph):
            continue

        name = glyph.smuflName

        metadata['glyphAdvanceWidths'][name] = glyph.advanceWidth
        metadata['glyphBBoxes'][name] = glyph.bBox

        if glyph.alternates:
            baseglyphs = {}
            baseglyphs['alternates'] = glyph.alternates
            metadata['glyphsWithAlternates'][name] = baseglyphs

        if glyph.anchors:
            metadata['glyphsWithAnchors'][name] = glyph.anchors

        if glyph.isLigature:
            metadata['ligatures'][name] = {}
            metadata['ligatures'][name]["codepoint"] = glyph.codepoint
            if glyph.components:
                metadata['ligatures'][name]['componentGlyphs'] = glyph.components
            metadata['ligatures'][name]["description"] = glyph.description

        if glyph.isOptional:
            metadata['optionalGlyphs'][name] = {}
            metadata['optionalGlyphs'][name]['codepoint'] = glyph.codepoint
            metadata['optionalGlyphs'][name]['description'] = glyph.description
            metadata['optionalGlyphs'][name]['classes'] = glyph.classes

        if glyph.isSet:
            sets[glyph.suffix] = _getSetTemplate()[glyph.suffix]
            glyphinfo = {"alternateFor": glyph.base.smuflName,
                         "codepoint": glyph.codepoint,
                         "description": glyph.description,
                         "name": glyph.smuflName}
            setglyphs.append(glyphinfo)
            metadata['sets'] = sets
            metadata['sets'][glyph.suffix]['glyphs'] = setglyphs

    return metadata


def _getSetTemplate() -> Dict[str, Dict[str, str]]:
    # Extract sets template from bravura_metadata.json.
    sets = {}
    metadata = Request(CONFIG['smufl.urls']['bravuraMetadataJson'],
                       CONFIG['smufl.paths']['bravuraMetadataJson']).json()
    for key, values in metadata['sets'].items():
        sets[key] = {}
        for subKey, value in values.items():
            if subKey not in ('description', 'type'):
                continue
            sets[key][subKey] = value
    return sets


if __name__ == '__main__':
    generateMetadata()
