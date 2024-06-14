#!/usr/bin/env python3
"""This script sets glyph anchors based on data from a SMuFL font metadata
JSON file (SMuFL's reference font, Bravura, by default).

This script requires that SMufoLib be installed within its
executive environment. It may also be imported as a module and contains
the following public funcitons:

    * :func:`importAnchors` – The scripts program function.
    * :func:`main` - Command line entry point.

"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any
import sys
import collections
from pathlib import Path

from smufolib.objects.font import Font
from smufolib.request import Request
from smufolib import cli, config

CONFIG = config.load()

# Parameter defaults
FONT_DATA = Request(CONFIG['metadata.paths']['referenceFont'],
                    CONFIG['metadata.fallbacks']['referenceFont'])
MARK = True
COLORS = CONFIG['color.anchors']
CLEAR = False
VERBOSE = False

# pylint: disable=invalid-name, too-many-arguments


def importAnchors(font: Font | Path | str = None,
                  fontData: Request | Path | str = FONT_DATA,
                  mark: bool = MARK,
                  colors: dict[str, tuple[int | float, int | float,
                                          int | float, int | float]] | None = COLORS,
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

    """
    fontData = fontData.json()
    if not isinstance(fontData, Request):
        fontData = Request(fontData).json()

    print('Preparing glyph data...')
    sourceAnchors = fontData['glyphsWithAnchors']
    names = {g.smufl.name: g.name for g in font if g.smufl.name
             and g.smufl.name in sourceAnchors}

    print('Processing...', end='\n\n')
    appended = collections.defaultdict(list)

    for smuflName, anchors in sourceAnchors.items():
        try:
            glyphName = names[smuflName]
        except KeyError:
            continue
        if clear:
            font[glyphName].rGlyph.clearAnchors()
        for anchorName, position in anchors.items():
            if mark and colors:
                anchorColor = colors.get(anchorName, None)
            font[glyphName].appendAnchor(anchorName, position, anchorColor)
            appended[f'{glyphName} ({smuflName})'].append(anchorName)

    font.save()
    if verbose:
        _printDiagnostics(appended)
    print('Done!')


def main():
    """Command line entry point."""
    args = _parseArgs()
    importAnchors(args.font, args.fontData,
                  args.color, args.clear, args.verbose)


def _printDiagnostics(results: dict[str, Any]) -> None:
    print('appended anchors:'.upper())
    for glyphName, anchors in results.items():
        print(f"\n\t{glyphName}:")
        for anchor in anchors:
            print(f"\t\t{anchor}")


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
