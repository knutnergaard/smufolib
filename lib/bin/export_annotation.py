#!/usr/bin/env python3
"""
Export SMufoLib glyph annotation to JSON file.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from smufolib import config
from smufolib.font import Font

CONFIG = config.configLoad()

# pylint: disable=invalid-name


def exportAnnotation(font: Font = Font(),
                     filepath: str | Path =
                     CONFIG['fontPaths']['annotationJsonOut']):
    """
    Export glyph annotation dictionaries to JSON file.
    """
    # Facilitate command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', default=font)
    parser.add_argument('--filepath', default=filepath)
    args = parser.parse_args()

    if not args.filepath:
        args.filepath = config.setDefaultPath(args.font, 'annotation.json')

    with open(args.filepath, 'w', encoding='utf-8') as jsonFile:
        notes = {}
        for glyph in args.font:
            if not glyph.annotation:
                continue

            notes[glyph.name] = glyph.annotation
            print(f'Exporting notation for glyph: {glyph.name}')

        json.dump(notes, jsonFile, indent=4, sort_keys=True)

    print('All done!')


if __name__ == '__main__':
    exportAnnotation()
