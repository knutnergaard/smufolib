#!/usr/bin/env python3
# coding: utf-8

"""This script checks font anchors against the metadata file of SMuFL's
reference font, Bravura, to find missing or superfluous glyph anchors
according to the SMuFL standard.

Discrepancies are printed to console, and glyphs may be marked with
color value specified in smufolib.cfg. Glyphs without annotated smufl
names or glyph names will be skipped.

This script requires that SMufoLib be installed within its executive
environment. It may also be imported as a module and contains the
following public funcitons:

    * :func:`checkAnchors` - The scripts program function.
    * :func:`main` – Command line entry point.

"""
from __future__ import annotations
from typing import Any
import argparse
from pathlib import Path

from tqdm import tqdm

from smufolib import Font, Request, cli, config, normalizers

CONFIG = config.load()

# Parameter defaults
FONT_DATA = Request(CONFIG['metadata.paths']['referenceFont'],
                    CONFIG['metadata.fallbacks']['referenceFont'])
MARK = False
MARK_COLOR = CONFIG['color.marks']['mark1']
VERBOSE = False

# pylint: disable=invalid-name


def checkAnchors(font: Font | Path | str,
                 fontData: Request | Path | str = FONT_DATA,
                 mark: bool = MARK,
                 color: tuple[int | float] | None = MARK_COLOR,
                 verbose: bool = VERBOSE) -> None:
    """Check validity of SMuFL-specific glyph anchors.

    :param font: Object or path to
     target :class:`~smufolib.objects.font.Font`.
    :param fontData: Object call or direct path to reference font
     metadata file. Defaults to :class:`~smufolib.request.Request`
     with :attr:`~smufolib.request.Request.path`
     and :attr:`~smufolib.request.Request.fallback` set to
     :ref:`[metadata.paths]` and :ref:`[metadata.fallbacks]` respective
     ``referenceFont`` configurations.
    :param mark: mark discrepant glyphs. Defaults to ``False``.
    :param color: Color value to apply when ``mark=True``.
     Defaults to
     :ref:`[color.marks]` ``mark1`` configuration.
     :param verbose: Make output verbose. Defaults to ``False``.

    """
    names = {}
    fontAnchors = {}
    referenceAnchors = {}
    if color is not None:
        color = normalizers.normalizeColor(color)

    # Convert font path to object.
    font = font if isinstance(font, Font) else Font(font)

    # Define print function to be do-nothing if verbose=False.
    verboseprint = print if verbose else lambda *a, **k: None

    # Build dicts of glyph names and anchors indexed on smufl names.
    print("Processing...")
    for glyph in tqdm(font):
        names[glyph.smufl.name] = glyph.name
        if not glyph.anchors:
            continue
        fontAnchors[glyph.smufl.name] = [a.name for a in glyph.anchors]

    # Get JSON from metadata path.
    try:
        metadata = fontData.json()
    except AttributeError:
        metadata = Request(fontData).json()

    # Build dict of reference anchors indexed on smufl names.
    for name, anchors in metadata['glyphsWithAnchors'].items():
        if name in fontAnchors:
            referenceAnchors[name] = anchors.keys()

    # Compare reference anchors to font anchors to get deficit.
    if not fontAnchors:
        verboseprint("\nNo anchors found.")
    else:
        verboseprint("\nMissing anchors:".upper(), end='\n\n')
        result = _evaluate(referenceAnchors, fontAnchors, names, verboseprint)
        if mark and color and result:
            for name in result:
                glyph = font[names[name]]
                glyph.markColor = color

        # Compare font anchors to reference anchors to get surplus.
        verboseprint("\nSuperfluous anchors:".upper(), end='\n\n')
        result = _evaluate(fontAnchors, referenceAnchors, names, verboseprint)
        if mark and color and result:
            for name in result:
                glyph = font[names[name]]
                glyph.markColor = color

        font.save()
        print("Done!")


def main():
    """Command line entry point."""
    args = _parseArgs()
    checkAnchors(args.font,
                 fontData=args.fontData,
                 mark=args.mark,
                 color=args.color,
                 verbose=args.verbose)


def _evaluate(test: dict[str:Any],
              reference: dict[str:Any],
              names: dict[str:str],
              verboseprint) -> list[str]:
    # Compare sources and print results.
    findings = []
    if not findings:
        verboseprint("None")
        return None

    for name, anchors in test.items():
        if name not in reference:
            continue

        for anchor in anchors:
            if anchor in reference[name]:
                continue

            if name not in findings:
                findings.append(name)
                verboseprint(f"\t{names[name]} ({name}):")
            verboseprint(f"\t\t{anchor}")

    return findings


def _parseArgs() -> argparse.Namespace:
    # Parse command line arguments and options.
    parser = cli.commonParser(
        'font',
        addHelp=True,
        description=(
            "Find missing or superfluous SMuFL anchors."),
        fontData=FONT_DATA,
        mark=MARK,
        color=MARK_COLOR,
        verbose=VERBOSE)
    return parser.parse_args()


if __name__ == '__main__':
    main()
