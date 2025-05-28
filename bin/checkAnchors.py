#!/usr/bin/env python3
"""Check SMuFL glyph anchors against reference font metadata.

This script checks font anchors against reference font metadata, identifying missing or
superfluous glyph anchors according to the SMuFL standard.

Discrepancies are printed to console, and glyphs may be marked with a specified color
value. Glyphs without annotated smufl names or glyph names will be skipped.

The script requires SMufoLib to be installed in its execution environment. It can be
used from the command line or as a Python module. See the :ref:`check-anchors-cli` and
:ref:`check-anchors-python` sections below for usage details.

"""

from __future__ import annotations
from typing import Any
import argparse
from pathlib import Path

from tqdm import tqdm

from smufolib import (
    Font,
    Request,
    cli,
    config,
    stdUtils,
)
from smufolib.utils.scriptUtils import normalizeColor as _normalizeColor
from smufolib.utils.scriptUtils import normalizeFont as _normalizeFont
from smufolib.utils.scriptUtils import normalizeJsonDict as _normalizeJsonDict
from smufolib.utils.scriptUtils import normalizeRequest as _normalizeRequest

# Type aliases
JsonDict = dict[str, Any]
ColorValue = int | float
ColorTuple = tuple[ColorValue, ColorValue, ColorValue, ColorValue]

# Configuration
CONFIG = config.load()

# Parameter defaults
FONT_DATA = Request(
    CONFIG["metadata.paths"]["font"],
    CONFIG["metadata.fallbacks"]["font"],
)
MARK = False
MARK_COLOR = CONFIG["color.marks"]["mark1"]
VERBOSE = False

# pylint: disable=invalid-name


def checkAnchors(
    font: Font | Path | str,
    fontData: Request | Path | str = FONT_DATA,
    mark: bool = MARK,
    color: ColorTuple | None = MARK_COLOR,
    verbose: bool = VERBOSE,
) -> None:
    """Check font anchors against SMuFL reference data (Python API).

    :param font: Target :class:`.Font` object or path to font file.
    :param fontData: Request for or path to reference font metadata file. Defaults to
        :class:`.Request` passing :confval:`metadata.paths.font` and
        :confval:`metadata.fallbacks.font`.
    :param mark: Mark discrepant glyphs. Defaults to :obj:`False`.
    :param color: Color to use when marking glyphs. Ignored unless ``mark=True``.
        Defaults to :confval:`color.marks.mark1`.
    :param verbose: Make output verbose. Defaults to :obj:`False`.
    :raises TypeError: If any parameter value is not the expected type or if `mark` is
        :obj:`True` while `color` is :obj:`None`.

    """
    print("Starting...")

    names = {}
    fontAnchors = {}
    referenceAnchors = {}
    font = _normalizeFont(font)
    metadata = _normalizeJsonDict(_normalizeRequest(fontData).json())
    color = _normalizeColor(color, mark)

    # Build dicts of glyph names and anchors indexed on smufl names.
    stdUtils.verbosePrint("\nCompiling font anchors...", verbose)
    for glyph in font if verbose else tqdm(font):
        names[glyph.smufl.name] = glyph.name
        if glyph.anchors:
            fontAnchors[glyph.smufl.name] = [a.name for a in glyph.anchors]

    if not fontAnchors:
        stdUtils.verbosePrint("\nNo font anchors found.", verbose)
    else:
        # Build dict of reference anchors indexed on smufl names.
        stdUtils.verbosePrint("\nCompiling reference anchors...", verbose)
        for name, anchors in metadata["glyphsWithAnchors"].items():
            if name in fontAnchors:
                referenceAnchors[name] = anchors.keys()

        # Compare reference anchors to font anchors to get deficit.
        stdUtils.verbosePrint("\nGlyphs with missing anchors:", verbose)
        result = _evaluate(referenceAnchors, fontAnchors, names, verbose)
        if mark and color and result:
            for name in result:
                glyph = font[names[name]]
                glyph.markColor = color

        # Compare font anchors to reference anchors to get surplus.
        stdUtils.verbosePrint("\nGlyphs with superfluous anchors:", verbose)
        result = _evaluate(fontAnchors, referenceAnchors, names, verbose)
        if mark and color and result:
            for name in result:
                glyph = font[names[name]]
                glyph.markColor = color

        print("\nDone.")


def main() -> None:
    """Command line entry point."""
    args = _parseArgs()
    checkAnchors(
        args.font,
        fontData=args.fontData,
        mark=args.mark,
        color=args.color,
        verbose=args.verbose,
    )


def _evaluate(
    test: JsonDict,
    reference: JsonDict,
    names: dict[str, str],
    verbose: bool,
) -> list[str]:
    # Compare sources and print results.
    findings: list[str] = []

    for name, anchors in test.items():
        if name not in reference:
            continue

        for anchor in anchors:
            if anchor in reference[name]:
                continue

            if name not in findings:
                findings.append(name)
                stdUtils.verbosePrint(f"\t'{names[name]}' ('{name}'):", verbose)
            stdUtils.verbosePrint(f"\t\t'{anchor}'", verbose)

    if not findings:
        stdUtils.verbosePrint("\tNone", verbose)

    return findings


def _parseArgs() -> argparse.Namespace:
    # Parse command line arguments and options.
    parser = cli.commonParser(
        "font",
        description=stdUtils.getSummary(__doc__),
        fontData=FONT_DATA,
        mark=MARK,
        color=MARK_COLOR,
        verbose=VERBOSE,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
