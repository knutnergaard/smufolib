#!/usr/bin/env python3
"""SMufoLib Check Anchors.

This script checks font anchors against the metadata file of SMuFL's
reference font, Bravura, to find missing or superfluous glyph anchors
according to the SMuFL standard.

Discrepancies are printed to console, and glyphs may be marked with
color value specified in smufolib.cfg. Glyphs without annotated smufl
names or glyph names will be skipped.

This script requires that `smufolib` be installed within its executive
environment. It may also be imported as a module and contains the
following public funcitons:

    * `checkAnchors` – main function of the script. See function help
        for parameter details.
"""
from __future__ import annotations
from typing import Any, Dict, List

from smufolib import Font, Request, cli, config

CONFIG = config.configLoad()

# pylint: disable=invalid-name


def checkAnchors(font: Font = Font(), mark: bool = False) -> None:
    """Build source dicts, executes evaluation.

    :param font: the script's target font object.
    :param mark: mark discrepant glyphs.
    """
    parser = cli.argParser(addHelp=True,
                           description=(
                               "Find missing or superfluous SMuFL anchors."),
                           font=font, mark=mark)
    args = parser.parse_args()

    names = {}
    fontAnchors = {}
    bravuraAnchors = {}

    # Build dicts of glyph names and anchors indexed on smuflnames.
    print('Processing...')
    for glyph in args.font:
        names[glyph.smuflName] = glyph.name
        if not glyph.rGlyph.anchors:
            continue
        fontAnchors[glyph.smuflName] = [a.name for a in glyph.rGlyph.anchors]

    # Build dict of bravura anchors indexed on smuflnames.
    metadata = Request(CONFIG['smufl.urls']['bravuraMetadataJson'],
                       CONFIG['smufl.paths']['bravuraMetadataJson']).json()
    for smuflName, anchors in metadata['glyphsWithAnchors'].items():
        if smuflName in fontAnchors:
            bravuraAnchors[smuflName] = anchors.keys()
    print('Done!', end='\n\n')

    # Compare bravura anchors to font anchors to get deficit.
    if not fontAnchors:
        print('No anchors found.')
    else:
        print('Missing anchors:'.upper(), end='\n\n')
        result = _evaluate(bravuraAnchors, fontAnchors, names)
        if args.mark:
            for smuflName in result:
                glyph = font[names[smuflName]]
                glyph.rGlyph.markColor = CONFIG['color.marks']['mark1']

        # Compare font anchors to bravura_anchors to get surplus.
        print('\nSuperfluous anchors:'.upper(), end='\n\n')
        result = _evaluate(fontAnchors, bravuraAnchors, names)
        if args.mark:
            for smuflName in result:
                glyph = font[names[smuflName]]
                glyph.rGlyph.markColor = CONFIG['color.marks']

        args.font.save()


def _evaluate(test: Dict[str:Any],
              reference: Dict[str:Any],
              names: Dict[str:str]) -> List[str]:
    # compares sources and prints results.
    findings = []
    if not findings:
        print('None')
        return

    for smuflName, anchors in test.items():
        if smuflName not in reference:
            continue

        for anchor in anchors:
            if anchor in reference[smuflName]:
                continue

            if smuflName not in findings:
                findings.append(smuflName)
                print(f'\t{names[smuflName]} ({smuflName}):')
            print(f'\t\t{anchor}')

    return findings


if __name__ == '__main__':
    checkAnchors()
