#!/usr/bin/env python3
"""SMufoLib Set Anchors.

This script sets glyph anchors based on data from a SMuFL font metadata
JSON file(SMuFL's reference font, Bravura, by default).

If `color` is True, anchors are colored based on the `AnchorColor`
section in smufolib.cfg. If `clear` is True, any preexisting anchor
points in the affected glyphs are erased before new ones are applied.
The names of any glyphs to exclude from the process may be specified in
`exclude`.

This script requires that `smufolib` be installed within its executive
environment. It may also be imported as a module and contains the
following public funcitons:

    * `setAnchors` – main function of the script. See function help
        for parameter details.
"""

from __future__ import annotations
from typing import Any, Dict
import collections

from smufolib import Font, Request, cli, config

CONFIG = config.configLoad()

# pylint: disable=invalid-name, too-many-arguments


def setAnchors(font: Font = Font(),
               fontData: Dict[str, Any]
               = Request(CONFIG['smufl.urls']['bravuraMetadataJson'],
                         CONFIG['smufl.paths']['bravuraMetadataJson']).json(),
               color: bool = True,
               clear: bool = True) -> None:
    """Append anchors to glyphs based on data from metadata.json file.

    :param font: font object to which the script applies.
    :param metadata: metadata source file in JSON format.
    :param color: apply anchor colors defined in `smufolib.cfg`.
    :param clear: erase preexisting anchors on append.
    """
    parser = cli.argParser(addHelp=True,
                           description=(
                               "Set anchors from font metadata JSON file."),
                           font=font, fontData=fontData,
                           color=color, clear=clear)
    args = parser.parse_args()

    print('Preparing glyph data...')
    sourceAnchors = args.fontData['glyphsWithAnchors']
    names = {g.smuflName: g.name for g in args.font if g.smuflName
             and g.smuflName in sourceAnchors}

    print('Processing...')
    appended = collections.defaultdict(list)

    for smuflName, anchors in sourceAnchors.items():
        try:
            glyphName = names[smuflName]
        except KeyError:
            continue
        if args.clear:
            args.font[glyphName].rGlyph.clearAnchors()
        for name, position in anchors.items():
            if args.color:
                anchorColor = CONFIG['color.anchors'].get(name, None)
            args.font[glyphName].appendAnchor(name, position, anchorColor)
            appended[f'{glyphName} ({smuflName})'].append(name)

    args.font.save()
    print('Done!', end='\n\n')
    _inform(appended)


def _inform(results: Dict[str, Any]) -> None:
    print('appended anchors:'.upper())
    for glyphName, anchors in results.items():
        print(f"\n\t{glyphName}:")
        for anchor in anchors:
            print(f"\t\t{anchor}")


if __name__ == '__main__':
    setAnchors()
