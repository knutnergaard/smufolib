#!/usr/bin/env python3
"""
Checks anchor point presence in SMuFL fonts.

Checks font anchors against Bravura metadata to find missing or
superfluous glyph anchors according to the SMuFL standard.

Discrepancies are printed to console, and glyphs may be marked with
color value specified in config.

Note: Glyphs without descriptive SMuFL names as notes or glyph
names will be skipped.
"""
import argparse
from smufolib.config import configLoad
from smufolib.font import Font
from smufolib.request import Request

CONFIG = configLoad()

# pylint: disable=invalid-name


def checkAnchors(mark: bool = False):
    """
    Builds source dicts, executes evaluation.

    :param mark: mark discrepant glyphs.
    """
    # Facilitate command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--mark', default=mark)
    args = parser.parse_args()

    font = Font()

    names = {}
    fontAnchors = {}
    bravuraAnchors = {}

    # Build dicts of glyph names and anchors indexed on smuflnames.
    print('Checking anchors...')
    for glyph in font:
        names[glyph.smuflName] = glyph.name
        if not glyph.rGlyph.anchors:
            continue
        fontAnchors[glyph.smuflName] = [a.name for a in glyph.rGlyph.anchors]

    # Build dict of bravura anchors indexed on smuflnames.
    metadata = Request(CONFIG['smuflUrls']['bravuraMetadataJson'],
                       CONFIG['smuflPaths']['bravuraMetadataJson']).json()
    for smuflName, anchors in metadata['glyphsWithAnchors'].items():
        if smuflName in fontAnchors:
            bravuraAnchors[smuflName] = anchors.keys()
    print('Done!\n')

    # Compare bravura anchors to font anchors to get deficit.
    if not fontAnchors:
        print('No anchors found!')
    else:
        print('Missing anchors'.upper())
        result = _evaluate(bravuraAnchors, fontAnchors, names)
        if args.mark:
            for smuflName in result:
                glyph = font[names[smuflName]]
                glyph.rGlyph.markColor = CONFIG['markColor']

        # Compare font anchors to bravura_anchors to get surplus.
        print('\nSuperfluous anchors:'.upper())
        result = _evaluate(fontAnchors, bravuraAnchors, names)
        if args.mark:
            for smuflName in result:
                glyph = font[names[smuflName]]
                glyph.rGlyph.markColor = CONFIG['markColor']

        font.save()


def _evaluate(test, reference, names):
    # compares sources and prints results.
    findings = []
    seen = set()
    for smuflName, anchors in test.items():
        if smuflName not in reference:
            continue

        for anchor in anchors:
            if anchor in reference[smuflName]:
                continue

            # Skip duplicates and print results.
            if smuflName not in seen:
                seen.add(smuflName)
                findings.append(smuflName)
                print(f'\n\t{names[smuflName]} ({smuflName}):')
            print(f'\t\t{anchor}')

    return findings


if __name__ == '__main__':
    checkAnchors()
