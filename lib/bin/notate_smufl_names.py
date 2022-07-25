#!/usr/bin/env python3
"""
Notate SmuflNames.
"""

from __future__ import annotations
import argparse

from smufolib import config, converters
from smufolib.font import Font
from smufolib.request import Request

CONFIG = config.configLoad()

# pylint: disable=invalid-name


def notateSmuflNames(font: Font = Font(), overwrite: bool = False):
    """
    Annotates glyph notes with SMuFL names.

    Preexisting names are skipped if overwrite is False and
    overwritten if True.
    """
    # Facilitate command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', default=font)
    parser.add_argument('--overwrite', default=overwrite)
    args = parser.parse_args()

    glyphmap = _buildGlyphMap()

    for glyph in args.font:
        if not glyph.rGlyph.unicode:
            print(f'Skipping unencoded glyph: {glyph.name}')
        if not args.overwrite and glyph.smuflName:
            print(f'Skipping prenamed glyph: {glyph.name}')
        for codepoint in glyph.rGlyph.unicodes:
            if codepoint not in glyphmap:
                continue
            print(f'Annotating glyph: {glyph.name}')
            glyph.smuflName = glyphmap[codepoint]

    args.font.save()
    print('All done!')


def _buildGlyphMap(metadata=Request(
        CONFIG['smuflUrls']['glyphnamesJson'],
        CONFIG['smuflPaths']['glyphnamesJson']).json()):
    # Build dictionary of codepoints mapped to smufl names.
    glyphmap = {}
    for name, data in metadata.items():
        codepoint = converters.toDecimal(data['codepoint'])
        glyphmap[codepoint] = name
    return glyphmap


if __name__ == '__main__':
    notateSmuflNames()
