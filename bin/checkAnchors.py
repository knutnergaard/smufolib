#!/usr/bin/env python3
# coding: utf-8
"""
This script checks font anchors against the metadata file of SMuFL's
reference font, Bravura, to find missing or superfluous glyph anchors
according to the SMuFL standard.

Discrepancies are printed to console, and glyphs may be marked with
color value specified in smufolib.cfg. Glyphs without annotated smufl
names or glyph names will be skipped.

This script requires SMufoLib to be installed within its executive
environment. It may also be imported as a module and contains the
following public funcitons:

    - :func:`checkAnchors` - The scripts program function.
    - :func:`main` – Command line entry point.

"""

from __future__ import annotations
from typing import Any
import argparse
from pathlib import Path

from tqdm import tqdm

from smufolib import Font, Request, cli, config, error, normalizers, stdUtils

# Type aliases
JsonDict = dict[str, Any]
ColorValue = int | float
ColorTuple = tuple[ColorValue, ColorValue, ColorValue, ColorValue]

# Configuration
CONFIG = config.load()

# Parameter defaults
FONT_DATA = Request(
    CONFIG["metadata.paths"]["referenceFont"],
    CONFIG["metadata.fallbacks"]["referenceFont"],
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
    """Check validity of SMuFL-specific glyph anchors.

    :param font: Object or path to
        target :class:`~smufolib.objects.font.Font`.
    :param fontData: Object call or direct path to reference font
        metadata file. Defaults to :class:`~smufolib.request.Request`
        with :attr:`~smufolib.request.Request.path`
        and :attr:`~smufolib.request.Request.fallback` set to
        :ref:`[metadata.paths]` and :ref:`[metadata.fallbacks]`
        respective `referenceFont` configurations.
    :param mark: mark discrepant glyphs. Defaults to :obj:`False`.
    :param color: Color value to apply when ``mark=True``.
        Defaults to :ref:`[color.marks]` `mark1` configuration.
    :param verbose: Make output verbose. Defaults to :obj:`False`.
    :raises TypeError: If any parameter value is not the expected type
        or if `mark` is :obj:`True` while `color` is :obj:`None`.

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


def _normalizeFont(font: Font | Path | str) -> Font:
    # Convert font path to object if necessary.
    error.validateType(font, (Font, Path, str), "font")
    if isinstance(font, Font):
        return font
    return Font(font)


def _normalizeRequest(request: Request | Path | str) -> Request:
    # Convert request path to object if necessary.
    error.validateType(request, (Request, Path, str), "request")
    if isinstance(request, Request):
        return request
    return Request(request)


def _normalizeJsonDict(jsonDict: JsonDict | None) -> JsonDict:
    # Ensure `jsonDict` is not None.
    if jsonDict is None:
        raise TypeError(error.generateTypeError(jsonDict, JsonDict, "JSON file"))
    return jsonDict


def _normalizeColor(color: ColorTuple | None, mark: bool) -> ColorTuple | None:
    # Normalize `color` value.
    if color is None:
        if mark:
            raise TypeError(
                error.generateTypeError(
                    value=color,
                    validTypes=tuple,
                    objectName="color",
                    dependencyInfo="'mark' is True",
                )
            )
        return None
    return normalizers.normalizeColor(color)


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
        description=stdUtils.getSummary(checkAnchors.__doc__),
        fontData=FONT_DATA,
        mark=MARK,
        color=MARK_COLOR,
        verbose=VERBOSE,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
