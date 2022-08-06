#!/usr/bin/env python3
"""SMufoLib Import Annotation.

This script imports annotation attributes from a source JSON file,
typically produced by the opposing `exportAnnotation` script, to a
SMufoLib font.

This script requires that `smufolib` be installed within its executive
environment. It may also be imported as a module and contains the
following public funcitons:

    * `importAnnotation` – main function of the script. See function help
        for parameter details.
"""
from __future__ import annotations
from typing import Tuple
from pathlib import Path
import json

from smufolib import Font, cli, config

CONFIG = config.configLoad()

# pylint: disable=invalid-name


def importAnnotation(font: Font = Font(),
                     source: str | Path =
                     CONFIG['font.paths']['annotationJsonIn'],
                     clear: bool = True,
                     overwrite: bool = True,
                     exclude: str | Tuple[str] | None = None) -> None:
    """Import glyph notes indexed on glyph names from JSON file.

    :param font: the script's target font object.
    :param source: filepath to source JSON file.
    :param clear: erase all preexisting glyph annotation on import.
    :param overwrite: overwrite preexisting annotation.
    :param exclude: glyphs to exclude from import.
    """
    parser = cli.argParser(addHelp=True,
                           descripiton=(
                               "Import annotation attributes from JSON file."),
                           font=font, source=source, clear=clear,
                           overwrite=overwrite, exclude=exclude)
    args = parser.parse_args()

    print("Locating source file...")
    if not args.source:
        args.source = Path(config.setDefaultPath(args.font, 'annotation.json'))
    if not args.source.is_file():
        raise FileNotFoundError("source file could not be found.")

    with open(args.source, encoding='utf-8') as jsonFile:
        for name, annotation in json.load(jsonFile).items():
            if name not in args.font:
                continue

            glyph = args.font[name]
            if args.clear:
                glyph.annotation = None

            toImport = {}
            for key, value in annotation.items():
                if args.exclude and key in args.exclude:
                    continue

                if not args.overwrite and key in glyph.annotation:
                    continue

                toImport[key] = value
            glyph.annotation = toImport
            print(f'Importing notation for glyph: {glyph.name}')

    args.font.save()
    print('Done!')


if __name__ == '__main__':
    importAnnotation()
