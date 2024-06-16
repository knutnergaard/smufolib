#!/usr/bin/env python3
# coding: utf-8
"""
This script sets glyph anchors based on data from a SMuFL font metadata
JSON file (SMuFL's reference font, Bravura, by default).

This script requires that SMufoLib be installed within its
executive environment. It may also be imported as a module and contains
the following public funcitons:

    * :func:`importAnchors` – The scripts program function.
    * :func:`main` - Command line entry point.

"""

from __future__ import annotations
from typing import Any
import collections
from pathlib import Path

from smufolib.objects.font import Font
from smufolib.request import Request
from smufolib import cli, config

from tqdm import tqdm

CONFIG = config.load()

# Parameter defaults
FONT_DATA = Request(CONFIG['metadata.paths']['referenceFont'],
                    CONFIG['metadata.fallbacks']['referenceFont'])
MARK = True
COLORS = CONFIG['color.anchors']
CLEAR = False
VERBOSE = False

# pylint: disable=invalid-name, too-many-arguments, too-many-locals


def importAnchors(font: Font | Path | str = None,
                  fontData: Request | Path | str = FONT_DATA,
                  mark: bool = MARK,
                  colors: dict[str, tuple[
                      int | float, int | float,
                      int | float, int | float]]
                  | None = COLORS,
                  clear: bool = CLEAR,
                  verbose: bool = VERBOSE) -> None:
    """Import anchors from font metadata.

    :param font: font object to which the script applies.
    :param fontData: Object call or direct path to reference font
     metadata file. Defaults to :class:`~smufolib.request.Request`
     with :attr:`~smufolib.request.Request.path`
     and :attr:`~smufolib.request.Request.fallback` set to
     :ref:`[metadata.paths]` and :ref:`[metadata.fallbacks]` respective
     ``referenceFont`` configurations.
    :param mark: Apply defined anchor colors. Defaults to ``True``
    :param colors: dict of anchorNames mapped to UFO color values to
     apply when ``mark=True``.
    :param clear: erase preexisting anchors on append. Defaults to
     ``False``.
     :param verbose: Make output verbose. Defaults to ``False``.

    """
    # Convert font path to object.
    font = font if isinstance(font, Font) else Font(font)

    # Define print function to be do-nothing if verbose=False.
    verboseprint = print if verbose else lambda *a, **k: None

    try:
        fontData = fontData.json()
    except AttributeError:
        fontData = Request(fontData).json()

    print('Preparing glyph data...')
    sourceAnchors = fontData['glyphsWithAnchors']
    names = {}
    for glyph in tqdm(font):
        if glyph.smufl.name and glyph.smufl.name in sourceAnchors:
            names[glyph.smufl.name] = glyph.name
    if not names:
        raise AttributeError(
            "Required Smufl glyph names are missing, "
            "concider running the importID script to add them.")

    print('Processing...', end='\n\n')
    for smuflName, anchors in sourceAnchors.items():
        try:
            glyphName = names[smuflName]
        except KeyError:
            continue
        if clear:
            font[glyphName].clearAnchors()
        verboseprint("Appending anchors to glyph:",
                     font.smufl.findGlyph(smuflName))
        for anchorName, position in anchors.items():
            if mark and colors:
                anchorColor = colors.get(anchorName, None)
            font[glyphName].appendAnchor(anchorName, position, anchorColor)
            verboseprint(f"\t{anchorName}")

    font.save()
    print('Done!')


def main():
    """Command line entry point."""
    args = _parseArgs()
    importAnchors(args.font, args.fontData,
                  args.color, args.clear, args.verbose)


def _parseArgs():
    # Parse command line arguments and options.
    parser = cli.commonParser('font',
                              addHelp=True,
                              description=(
                                  "Set anchors from font metadata JSON file."),
                              fontData=FONT_DATA,
                              mark=MARK,
                              colors=COLORS,
                              clear=CLEAR,
                              verbose=VERBOSE)
    return parser.parse_args()


if __name__ == '__main__':
    main()
