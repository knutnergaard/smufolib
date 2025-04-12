#!/usr/bin/env python3
# coding: utf-8
"""
This script sets glyph anchors based on data from a SMuFL font metadata
JSON file (SMuFL's reference font, Bravura, by default).

This script requires SMufoLib to be installed within its
executive environment. It may also be imported as a module and contains
the following public funcitons:

    - :func:`importAnchors` – The scripts program function.
    - :func:`main` - Command line entry point.

"""

from __future__ import annotations
from typing import Any
import argparse
from contextlib import nullcontext
from pathlib import Path
import time

from tqdm import tqdm

from smufolib.objects.font import Font
from smufolib.request import Request
from smufolib import cli, config
from smufolib.utils import error, normalizers, stdUtils
from smufolib.utils.scriptUtils import normalizeFont as _normalizeFont
from smufolib.utils.scriptUtils import normalizeJsonDict as _normalizeJsonDict
from smufolib.utils.scriptUtils import normalizeRequest as _normalizeRequest


JsonDict = dict[str, Any]
ColorValue = int | float
ColorTuple = tuple[ColorValue, ColorValue, ColorValue, ColorValue]
ColorDict = dict[str, ColorTuple]

CONFIG = config.load()

# Parameter defaults
FONT_DATA = Request(
    CONFIG["metadata.paths"]["referenceFont"],
    CONFIG["metadata.fallbacks"]["referenceFont"],
)
MARK = True
COLORS = CONFIG["color.anchors"]
CLEAR = False
VERBOSE = False

# pylint: disable=invalid-name, too-many-arguments, too-many-locals


def importAnchors(
    font: Font | Path | str,
    fontData: Request | Path | str = FONT_DATA,
    mark: bool = MARK,
    colors: ColorDict | None = COLORS,
    clear: bool = CLEAR,
    verbose: bool = VERBOSE,
) -> None:
    """Import anchors from font metadata.

    :param font: font object to which the script applies.
    :param fontData: Object call or direct path to reference font
        metadata file. Defaults to :class:`~smufolib.request.Request`
        with :obj:`~smufolib.request.Request.path`
        and :obj:`~smufolib.request.Request.fallback` set to
        :ref:`[metadata.paths]` and :ref:`[metadata.fallbacks]` respective
        `referenceFont` configurations.
    :param mark: Apply defined anchor colors. Defaults to :obj:`True`
    :param colors: dict of anchorNames mapped to UFO color values to
        apply when `mark` is :obj:`True`.
    :param clear: erase preexisting anchors on append. Defaults to
        :obj:`False`.
    :param verbose: Make output verbose. Defaults to :obj:`False`.
    :raises TypeError: If any parameter value is not the expected type
        or if `mark` is :obj:`True` while `colors` is :obj:`None`.
    :raises AttributeError: if required values for :attr:`.Smufl.name`
        are missing.

    """
    print("Starting...")

    font = _normalizeFont(font)
    metadata = _normalizeJsonDict(_normalizeRequest(fontData).json())
    colors = _normalizeColorDict(colors, mark)
    sourceAnchors = metadata["glyphsWithAnchors"]

    ticks = len(font) + len(sourceAnchors) + 1
    with tqdm(total=ticks) if not verbose else nullcontext() as progressBar:
        stdUtils.verbosePrint("\nCompiling glyph data...", verbose)
        names = {}
        for glyph in font:
            if progressBar:
                progressBar.update(1)
                time.sleep(0.0001)

            if glyph.smufl.name and glyph.smufl.name in sourceAnchors:
                names[glyph.smufl.name] = glyph.name

        if not names:
            raise ValueError(
                error.generateErrorMessage(
                    "missingValue",
                    "recommendScript",
                    objectName="Smufl.name",
                    scriptName="importID",
                )
            )

        for smuflName, anchors in sourceAnchors.items():
            if progressBar:
                progressBar.update(1)
                time.sleep(0.0001)

            try:
                glyphName = names[smuflName]
            except KeyError:
                continue
            if clear:
                font[glyphName].clearAnchors()
            stdUtils.verbosePrint(
                f"\nAppending anchors to glyph '{glyphName}':",
                verbose,
            )
            for anchorName, position in anchors.items():
                position = [font.smufl.toUnits(p) for p in position]

                anchorColor = colors.get(anchorName) if mark and colors else None
                font[glyphName].appendAnchor(anchorName, position, anchorColor)
                stdUtils.verbosePrint(f"\t{anchorName}", verbose)

        font.save()
        if progressBar:
            progressBar.update(1)
            time.sleep(0.0001)

    print("\nDone.")


def main() -> None:
    """Command line entry point."""
    args = _parseArgs()
    importAnchors(
        args.font,
        fontData=args.fontData,
        mark=args.mark,
        colors=args.colors,
        clear=args.clear,
        verbose=args.verbose,
    )


def _normalizeColorDict(colorDict: ColorDict | None, mark: bool) -> ColorDict | None:
    # Normalize dict of color values.
    if colorDict is None:
        if mark:
            raise TypeError(
                error.generateTypeError(
                    value=colorDict,
                    validTypes=ColorDict,
                    objectName="colors",
                    dependencyInfo="'mark' is True",
                )
            )
        return None

    error.validateType(colorDict, dict, "colors")
    for value in colorDict.values():
        normalizers.normalizeColor(value)

    return colorDict


def _parseArgs() -> argparse.Namespace:
    # Parse command line arguments and options.
    parser = cli.commonParser(
        "font",
        description=stdUtils.getSummary(importAnchors.__doc__),
        fontData=FONT_DATA,
        mark=MARK,
        colors=COLORS,
        clear=CLEAR,
        verbose=VERBOSE,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
