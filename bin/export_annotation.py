#!/usr/bin/env python3
"""SMufoLib Export Annotation.

This script exports annotation attributes (by way of the dictionary
string assigned to the note field of each glyph) as a JSON file, to be
imported to another SMufoLib font with the opposing `importAnnotation`
script.

This script requires that `smufolib` be installed within its executive
environment. It may also be imported as a module and contains the
following public funcitons:

    * `exportAnnotation` – main function of the script. See function help
        for parameter details.
"""
from __future__ import annotations
from pathlib import Path
import json

from smufolib import Font, cli, config

CONFIG = config.configLoad()

# pylint: disable=invalid-name


def exportAnnotation(font: Font = Font(),
                     target: str | Path =
                     CONFIG['font.paths']['annotationJsonOut']) -> None:
    """Export glyph annotation dictionaries to JSON file.

    :param font: the script's target font object.
    :param target: filepath to created target JSON file.
    """
    parser = cli.argParser(addHelp=True,
                           descripiton=(
                               "Export annotation attributes to JSON file."),
                           font=font, target=target)
    args = parser.parse_args()

    if not args.target:
        args.target = config.setDefaultPath(args.font, 'annotation.json')

    print("Creating file...")
    with open(args.target, 'w', encoding='utf-8') as jsonFile:
        notes = {}
        for glyph in args.font:
            if not glyph.annotation:
                continue

            notes[glyph.name] = glyph.annotation
            print(f'Exporting annotation for glyph: {glyph.name}')

        print(f'Writing annotation to: {args.target}')
        json.dump(notes, jsonFile, indent=4, sort_keys=True)

    print('Done!')


if __name__ == '__main__':
    exportAnnotation()
