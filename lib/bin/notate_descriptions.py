#!/usr/bin/env python3
"""
Notate Descriptions
"""

from __future__ import annotations
import argparse

from smufolib import config
from smufolib.font import Font
from smufolib.request import Request

CONFIG = config.configLoad()

# pylint: disable=invalid-name


def notateDescriptions(font: Font = Font(), overwrite: bool = False):
    """
    Appends description to glyph notes.
    """
    # Facilitate command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', default=font)
    parser.add_argument('--overwrite', default=overwrite)
    args = parser.parse_args()

    descriptions = _buildDescriptions()

    for glyph in args.font:
        if glyph.rGlyph.unicode and glyph.rGlyph.unicode < 0xF400:
            continue

        if not glyph.rGlyph.unicode:
            print(f'Skipping unencoded glyph: {glyph.name}')
        elif not args.overwrite and glyph.description:
            print(f'Skipping predescribed glyph: {glyph.name}')
        elif glyph.smuflName not in descriptions:
            print(f'Unable to lookup description for glyph: {glyph.name}')
        else:
            print(f'Annotating glyph: {glyph.name}')
            glyph.description = descriptions[glyph.smuflName]

    args.font.save()
    print('All done!')


def _buildDescriptions(metadata=Request(
        CONFIG['smuflUrls']['bravuraMetadataJson'],
        CONFIG['smuflPaths']['bravuraMetadataJson']).json()):
    # Build dictionary of names mapped to descriptions.
    descriptions = {}
    for structure, smuflNames in metadata.items():
        if structure not in ('ligatures', 'optionalGlyphs', 'sets'):
            continue
        for smuflName, values in smuflNames.items():
            if 'description' not in values:
                continue
            descriptions[smuflName] = values['description']
    return descriptions


if __name__ == '__main__':
    notateDescriptions()
