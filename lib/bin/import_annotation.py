#!/usr/bin/env python3
"""
Import SMufoLib glyph annotation from JSON file.
"""
from __future__ import annotations
from typing import Tuple
import argparse
import json
from pathlib import Path

from smufolib import config
from smufolib.font import Font

CONFIG = config.configLoad()

# pylint: disable=invalid-name


def importAnnotation(font: Font = Font(),
                     filepath: str | Path =
                     CONFIG['fontPaths']['annotationJsonIn'],
                     reset: bool = True,
                     exclude: str | Tuple[str] | None = None,
                     overwrite: bool = True):
    """
    Imports glyph notes indexed on glyph names from JSON file.
    """
    # Facilitate command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', default=font)
    parser.add_argument('--filepath', default=filepath)
    parser.add_argument('--reset', default=reset)
    parser.add_argument('--exclude', default=exclude)
    parser.add_argument('--overwrite', default=overwrite)
    args = parser.parse_args()

    args.filepath = config.setDefaultPath(args.font, 'annotation.json')
    with open(args.filepath, encoding='utf-8') as jsonFile:
        for name, annotation in json.load(jsonFile).items():
            if name not in args.font:
                continue

            glyph = args.font[name]
            if args.reset:
                glyph.annotation = None

            toImport = {}
            for key, value in annotation.items():
                if args.exclude:
                    if key == args.exclude or key in args.exclude:
                        continue

                if not args.overwrite and key in glyph.annotation:
                    continue

                toImport[key] = value
            glyph.annotation = toImport
            print(f'Importing notation for glyph: {glyph.name}')

    args.font.save()
    print('All done!')


if __name__ == '__main__':
    importAnnotation()
