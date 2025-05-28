#!/usr/bin/env python3
# coding: utf-8
"""Import anchors from font metadata.

This script sets glyph anchors based on data from a SMuFL font metadata JSON file
(SMuFL's reference font, Bravura, by default).

The script requires SMufoLib to be installed in its execution environment. It can be
used from the command line or as a Python module. See the :ref:`import-anchors-cli`
and :ref:`import-anchors-python` sections below for usage details.

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
from smufolib.utils import error, stdUtils
from smufolib.utils.scriptUtils import normalizeFont as _normalizeFont
from smufolib.utils.scriptUtils import normalizeJsonDict as _normalizeJsonDict
from smufolib.utils.scriptUtils import normalizeRequest as _normalizeRequest
from smufolib.utils.scriptUtils import normalizeColorDict as _normalizeColorDict


JsonDict = dict[str, Any]
ColorValue = int | float
ColorTuple = tuple[ColorValue, ColorValue, ColorValue, ColorValue]
ColorDict = dict[str, ColorTuple]

CONFIG = config.load()

# Parameter defaults
FONT_DATA = Request(
    CONFIG["metadata.paths"]["font"],
    CONFIG["metadata.fallbacks"]["font"],
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
    """Import anchors from font metadata (Python API).

    :param font: Target :class:`.Font` object or path to font file.
    :param fontData: Request for or path to reference font metadata file.
        Defaults to :class:`.Request` passing
        :confval:`metadata.paths.font` and :confval:`metadata.fallbacks.font`.
    :param mark: Apply defined anchor colors. Defaults to :obj:`True`.
    :param colors: dict of anchorNames mapped to UFO color values to
        apply when `mark` is :obj:`True`. Defaults to :confval:`color.anchors`.
    :param clear: Erase preexisting anchors on append. Defaults to
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

            glyphName = names.get(smuflName)
            if not glyphName:
                continue

            if clear:
                font[glyphName].clearAnchors()

            stdUtils.verbosePrint(
                f"\nAppending anchors to glyph '{glyphName}' ('{smuflName}'):",
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


def _parseArgs() -> argparse.Namespace:
    # Parse command line arguments and options.
    parser = cli.commonParser(
        "font",
        description=stdUtils.getSummary(__doc__),
        fontData=FONT_DATA,
        mark=MARK,
        colors=COLORS,
        clear=CLEAR,
        verbose=VERBOSE,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
