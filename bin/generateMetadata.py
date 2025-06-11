#!/usr/bin/env python3
# pylint: disable=C0301
"""Generate font metadata JSON file.

This script generates a full featured metadata `JSON
<https://www.json.org/json-en.html>`_ file for SMuFL fonts from metadata sources and
user specifications, including the following metadata sections:

    - :smufl:`mandatory (fontName and fontVersion) <specification/font-specific-metadata.html>`
    - :smufl:`size <specification/font-specific-metadata.html>`
    - :smufl:`engravingDefaults <specification/engravingdefaults.html>`
    - :smufl:`glyphAdvanceWidths <specification/glyphadvancewidths.html>`
    - :smufl:`glyphsWithAnchors <specification/glyphswithanchors.html>`
    - :smufl:`glyphsWithAlternates <specification/glyphswithalternates.html>`
    - :smufl:`glyphBBoxes <specification/glyphbboxes.html>`
    - :smufl:`ligatures <specification/ligatures.html>`
    - :smufl:`sets <specification/sets.html>`
    - :smufl:`optionalGlyphs <specification/optionalglyphs.html>`

Sections are automatically added depending on the font's scope and assigned attribute
values.

.. tip::

    As a starting point, identification and engraving defaults
    attributes may be set automatically with the :mod:`~bin.importID`
    and :mod:`~bin.calculateEngravingDefaults` scripts respectively.

Glyphs outside the SMuFL range as well as unencoded or unnamed glyphs, are automatically
skipped.

The script requires SMufoLib to be installed in its execution environment. It can be
used from the command line or as a Python module. See the :ref:`generate-metadata-cli`
and :ref:`generate-metadata-python` sections below for usage details.

"""

from __future__ import annotations
from typing import Any
import argparse
import collections
from pathlib import Path

from tqdm import tqdm

from smufolib import Font, config
from smufolib.request import Request, writeJson
from smufolib import cli
from smufolib.utils import stdUtils
from smufolib.utils.scriptUtils import normalizeFont as _normalizeFont
from smufolib.utils.scriptUtils import normalizeJsonDict as _normalizeJsonDict
from smufolib.utils.scriptUtils import normalizeRequest as _normalizeRequest
from smufolib.utils.scriptUtils import normalizeTargetPath as _normalizeTargetPath

# Type aliases
JsonDict = dict[str, Any]
SetsTemplate = dict[str, dict[str, str]]

# Configuration
CONFIG = config.load()

# Parameter defaults
FONT_DATA = Request(
    CONFIG["metadata.paths"]["font"],
    CONFIG["metadata.fallbacks"]["font"],
)
VERBOSE = False

# pylint: disable=C0103


def generateMetadata(
    font: Font | Path | str,
    targetPath: str | Path,
    fontData: str | Path | Request = FONT_DATA,
    verbose: bool = VERBOSE,
) -> None:
    """Generate font metadata JSON file (Python API).

    :param font: Source :class:`.Font` object or path to font file.
    :param targetPath: Target directory for Metadata JSON file.
    :param fontData: Request for or path to reference font metadata file.
        Defaults to :class:`.Request` passing
        :confval:`metadata.paths.font` and :confval:`metadata.fallbacks.font`.
    :param verbose: Make output verbose. Defaults to :obj:`False`.
    :raises TypeError: If any parameter value is not the expected type.
    :raises FileNotFoundError: If `targetPath` does not exist.

    """
    print("Starting...")

    targetPath = _normalizeTargetPath(targetPath)
    font = _normalizeFont(font)
    fontDataJson = _normalizeJsonDict(_normalizeRequest(fontData).json())
    font.smufl.spaces = True

    metadata = _compileMetadata(font, fontDataJson, verbose)

    filename = targetPath.resolve() / f"{font.smufl.name}.json"
    stdUtils.verbosePrint(f"\nWriting metadata to: '{filename}'", verbose)
    writeJson(filename, metadata)

    print("\nDone.")


def main() -> None:
    """Command line entry point."""
    args = _parseArgs()
    generateMetadata(
        args.font, args.targetPath, fontData=args.fontData, verbose=args.verbose
    )


def _compileMetadata(font: Font, fontData: JsonDict, verbose: bool) -> JsonDict:
    # Build SMuFL-specific metadata dictionary.
    # pylint: disable=R0912, R0914
    stdUtils.verbosePrint("\nCompiling font metadata...", verbose)

    metadata: collections.defaultdict[str, JsonDict] = collections.defaultdict(dict)

    keys = ("fontName", "fontVersion", "designSize", "sizeRange", "engravingDefaults")

    for key in keys:
        attribute = key[4:].lower() if "font" in key else key
        value = getattr(font.smufl, attribute)
        if attribute == "engravingDefaults":
            value = value.items()
        elif value is None:
            continue
        metadata[key] = value

    sets, setGlyphs = {}, []
    setsTemplate = _getSetsTemplate(fontData)

    stdUtils.verbosePrint("\nCompiling metadata for glyphs:", verbose)
    for glyph in font if verbose else tqdm(font):
        if glyph is None or not stdUtils.validateAttr(
            glyph, ("name", "unicode", "smufl.isMember")
        ):
            stdUtils.verbosePrint("\tSkipping invalid glyph:", verbose, glyph)
            continue
        stdUtils.verbosePrint(f"\t{glyph}", verbose)

        s = glyph.smufl
        metadata["glyphAdvanceWidths"][s.name] = s.advanceWidth
        metadata["glyphBBoxes"][s.name] = s.bBox

        if s.alternates:
            metadata["glyphsWithAlternates"][s.name] = {"alternates": s.alternates}

        if s.anchors:
            metadata["glyphsWithAnchors"][s.name] = s.anchors

        if s.isLigature:
            metadata["ligatures"][s.name] = {
                "codepoint": s.codepoint,
                "componentGlyphs": s.componentNames,
                "description": s.description,
            }

        if s.isOptional:
            metadata["optionalGlyphs"][s.name] = {
                "codepoint": s.codepoint,
                "description": s.description,
                "classes": s.classes,
            }

        if s.isSet:
            sets[s.suffix] = setsTemplate[s.suffix]
            glyphInfo = {
                "alternateFor": s.base.smufl.name,
                "codepoint": s.codepoint,
                "description": s.description,
                "name": s.name,
            }
            setGlyphs.append(glyphInfo)
            metadata["sets"] = sets
            metadata["sets"][s.suffix]["glyphs"] = setGlyphs

    return metadata


def _getSetsTemplate(fontData: JsonDict) -> SetsTemplate:
    # Extract sets template from bravura_metadata.json.
    sets: dict[str, dict[str, str]] = {}

    for key, values in fontData["sets"].items():
        sets[key] = {}
        for subKey, value in values.items():
            if subKey not in ("description", "type"):
                continue
            sets[key][subKey] = value
    return sets


def _parseArgs() -> argparse.Namespace:
    # Parse command line arguments and options.
    parser = cli.commonParser(
        "font",
        "targetPath",
        description=stdUtils.getSummary(__doc__),
        fontData=FONT_DATA,
        verbose=VERBOSE,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
