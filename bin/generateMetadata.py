#!/usr/bin/env python3
# coding: utf-8

# pylint: disable=C0301

"""This script generates a full featured metadata `JSON
<https://www.json.org/json-en.html>`_ file for SMuFL fonts from
metadata sources and user specifications, including the following
metadata sections:

    * `mandatory (fontName and fontVersion)
      <https://w3c.github.io/smufl/latest/specification/font-specific-metadata.html>`_
    * `size <https://w3c.github.io/smufl/latest/specification/font-specific-metadata.html>`_
    * `engravingDefaults <https://w3c.github.io/smufl/latest/specification/engravingdefaults.html>`_
    * `glyphAdvanceWidths <https://w3c.github.io/smufl/latest/specification/glyphadvancewidths.html>`_
    * `glyphsWithAnchors <https://w3c.github.io/smufl/latest/specification/glyphswithanchors.html>`_
    * `glyphsWithAlternates <https://w3c.github.io/smufl/latest/specification/glyphswithalternates.html>`_
    * `glyphBBoxes <https://w3c.github.io/smufl/latest/specification/glyphbboxes.html>`_
    * `ligatures <https://w3c.github.io/smufl/latest/specification/ligatures.html>`_
    * `sets <https://w3c.github.io/smufl/latest/specification/sets.html>`_
    * `optionalGlyphs <https://w3c.github.io/smufl/latest/specification/optionalglyphs.html>`_

Sections are automatically added depending on the font's scope and
assigned values.

This script requires that SMufoLib be installed within its executive
environment. It may also be imported as a module and contains the
following public functions:

    * :func:`generateMetadata` – The scripts program function.
    * :func:`main` - Command line entry point.

"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any
import argparse
import collections
from pathlib import Path
import json

from tqdm import tqdm

from smufolib import Font, Request, cli, config, stdUtils

CONFIG = config.load()

# Parameter defaults
FONT_DATA = Request(CONFIG['metadata.paths']['referenceFont'],
                    CONFIG['metadata.fallbacks']['referenceFont'])
VERBOSE = False

# pylint: disable=C0103


def generateMetadata(font: Font | Path | str,
                     targetPath: str | Path,
                     fontData: str | Path | Request = FONT_DATA,
                     verbose: bool = VERBOSE) -> None:
    """Generate metadata JSON file.

    :param font: Object or path to
     targetPath :class:`~smufolib.objects.font.Font`.
    :param targetPath: Target directory for Metadata JSON file.
    :param verbose: Make output verbose. Defaults to ``False``.

    """
    # Check if targetPath exists.
    if not Path(targetPath).exists():
        raise FileNotFoundError("Target path does not exist.")

    # Convert font path to object.
    font = font if isinstance(font, Font) else Font(font)

    # Define print function to be do-nothing if verbose=False.
    verboseprint = print if verbose else lambda *a, **k: None

    metadata = _compileMetadata(font, fontData, verbose, verboseprint)
    filename = Path(targetPath).resolve() / f'{font.smufl.name}_metadata.json'

    verboseprint("Writing metadata to:", filename)
    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(metadata, outfile, indent=4, sort_keys=False)

    print("Done!")


def main():
    """Command line entry point."""
    args = _parseArgs()
    generateMetadata(args.font,
                     args.targetPath,
                     fontData=args.fontData,
                     verbose=args.verbose)


def _compileMetadata(font, fontData, verbose, verboseprint) -> dict[str, Any]:
    # Build SMuFL-specific metadata dictionary.
    # pylint: disable=R0912, R0914

    print("Compiling metadata...")

    metadata = collections.defaultdict(dict)

    keys = ('fontName', 'fontVersion', 'designSize',
            'sizeRange', 'engravingDefaults')

    for key in keys:
        attribute = key[4:].lower() if 'font' in key else key
        value = getattr(font.smufl, attribute)
        if attribute == 'engravingDefaults':
            value = value.items()
        elif value is None:
            continue
        metadata[key] = value

    sets, setglyphs = {}, []
    setsTemplate = _getSetsTemplate(fontData)
    attributes = ('name', 'unicode')
    # Set up progress bar if verbose is True
    font = font if verbose else tqdm(font)
    # skipped = []

    for glyph in font:
        if not glyph or not stdUtils.validateClassAttr(glyph, attributes):
            verboseprint("Skipping unnamed or unencoded glyph:", glyph)
            continue

        s = glyph.smufl
        metadata['glyphAdvanceWidths'][s.name] = s.advanceWidth
        metadata['glyphBBoxes'][s.name] = s.bBox

        if s.alternates:
            baseglyphs = {}
            baseglyphs['alternates'] = s.alternates
            metadata['glyphsWithAlternates'][s.name] = baseglyphs

        if s.anchors:
            metadata['glyphsWithAnchors'][s.name] = s.anchors

        if s.isLigature:
            metadata['ligatures'][s.name] = {}
            metadata['ligatures'][s.name]["codepoint"] = s.codepoint
            if s.componentGlyphs:
                metadata['ligatures'][s.name]['componentGlyphs'] = s.componentGlyphs
            metadata['ligatures'][s.name]["description"] = s.description

        if s.isOptional:
            metadata['optionalGlyphs'][s.name] = {}
            metadata['optionalGlyphs'][s.name]['codepoint'] = s.codepoint
            metadata['optionalGlyphs'][s.name]['description'] = s.description
            metadata['optionalGlyphs'][s.name]['classes'] = s.classes

        if s.isSet:
            sets[s.suffix] = setsTemplate[s.suffix]
            glyphinfo = {"alternateFor": s.base.name,
                         "codepoint": s.codepoint,
                         "description": s.description,
                         "name": s.name}
            setglyphs.append(glyphinfo)
            metadata['sets'] = sets
            metadata['sets'][s.suffix]['glyphs'] = setglyphs

    return metadata


def _getSetsTemplate(fontData) -> dict[str, dict[str, str]]:
    # Extract sets template from bravura_metadata.json.
    sets = {}
    metadata = fontData.json()
    for key, values in metadata['sets'].items():
        sets[key] = {}
        for subKey, value in values.items():
            if subKey not in ('description', 'type'):
                continue
            sets[key][subKey] = value
    return sets


def _parseArgs() -> argparse.Namespace:
    # Parse command line arguments and options.
    parser = cli.commonParser('font',
                              'targetPath',
                              addHelp=True,
                              description="Generate font metadata JSON file.",
                              fontData=FONT_DATA,
                              verbose=VERBOSE)

    return parser.parse_args()


if __name__ == '__main__':
    main()
