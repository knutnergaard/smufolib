#!/usr/bin/env python3
"""SMufoLib Set Annotation.

This script sets specified annotation attributes, smuflName
(i.e, canonical glyph name), classes and/or description, for the glyphs
in a SMufoLib font. If `includeOptionals` is True, annotation for
optional glyphs, including ligatures, will be set. Please beware that
this assumes an equivalent encoding scheme to that of SMuFL's reference
font, Bravura.

The script derives its classification of optional glyphs from the
primary classes in `classes.json`. This requires that all optional
glyphs be named with reference to their base glyph, in accordance with
the `Adobe Glyph List Specification
<https://github.com/adobe-type-tools/agl-specification>`_.

Each attribute is set as a key-value pair in a dictionary-formatted
string, assigned to the base font's note field, `Glyph.rGlyph.note`.

If `overwrite` is False, annotation is skipped for glyphs with malformed
note field or preset attributes. Annotation is also skipped if glyph is
unencoded or if lookup fails(usually because the decimal codepoint does
not exist in the source metadata.

This script requires that `smufolib` be installed within its executive
environment. It may also be imported as a module and contains the
following public functions:

    * `setAnnotation` – main function of the script. See function help
        for parameter details.
"""

from __future__ import annotations
from typing import Any, Dict, List
from collections.abc import Iterable
import argparse
import ast
import collections

from smufolib import Font, Glyph, Request, cli, config, converters

CONFIG = config.configLoad()

# pylint: disable=invalid-name, too-many-arguments


def setAnnotation(font: Font = Font(),
                  classData: Dict[str, List[str]]
                  = Request(CONFIG['smufl.urls']['classesJson'],
                            CONFIG['smufl.paths']['classesJson']).json(),
                  glyphnameData: Dict[str, Dict[str, str]]
                  = Request(CONFIG['smufl.urls']['glyphnamesJson'],
                            CONFIG['smufl.paths']['glyphnamesJson']).json(),
                  fontData: Dict[str, Any]
                  = Request(CONFIG['smufl.urls']['bravuraMetadataJson'],
                            CONFIG['smufl.paths']['bravuraMetadataJson']).json(),
                  keys: str | Iterable[str] = ('classes'),
                  includeOptionals: bool = False,
                  overwrite: bool = False) -> None:
    """Append description to glyph notes.

    Glyphs that are either unencoded, outside SMuFL's recommended and
    optional ranges (U+E000-U+F8FF) or missing on lookup are always
    skipped. Glyphs with preexisting descriptions are skipped if
    overwrite is False and overwritten if True.

    :param font: the script's target font object.
    :param classesData: metadata source for classes.
    :param glyphnameData: metadata source for name and description.
    :param fontData: metadata source for optional glyphs.
    :param keys: annotation keys to be set. Value can be either
        'name' (i.e., SMuFL-specific canonical glyph name), 'classes',
        'description' or tuple of several.
    :param overwrite: overwrite any preexisting names or malformatted
        glyph note fields.
    :param includeOptionals: set annotation for optional glyphs.
    """
    args = _parseArgs(font, classData, glyphnameData, fontData,
                      keys, includeOptionals, overwrite)

    glyphMaps = _buildGlyphMaps(args.font, args.keys,
                                args.includeOptionals, args.classData,
                                args.glyphnameData, args.fontData)

    results = collections.defaultdict(list)
    results['lookupError'] = collections.defaultdict(list)
    results['annotated'] = collections.defaultdict(list)

    print("Processing...")
    for glyph in args.font:
        if not glyph.name.startswith('uni'):
            continue
        codepoint = glyph.rGlyph.unicode
        if not codepoint:
            results['unencoded'].append(glyph.name)
            continue

        for key in args.keys:
            designations = {'name': 'prenamed',
                            'classes': 'preclassified',
                            'description': 'predescribed'}

            if codepoint not in glyphMaps[key]:
                results['lookupError'][key].append(glyph.name)
                continue

            attribute = 'smuflName' if key == 'name' else key
            try:
                isinstance(ast.literal_eval(glyph.rGlyph.note), dict)
                if glyph.annotation.get(key) and not args.overwrite:
                    results[designations][key].append(glyph.name)
                    continue

                setattr(glyph, attribute, glyphMaps[key][codepoint])
                results['annotated'][key].append(glyph.name)

            except (SyntaxError, ValueError, TypeError):
                if glyph.rGlyph.note and not args.overwrite:
                    if glyph.name not in results['malformatted']:
                        results['malformatted'].append(glyph.name)
                    continue

                glyph.annotation = {}
                setattr(glyph, attribute, glyphMaps[key][codepoint])
                results['annotated'][key].append(glyph.name)

    args.font.save()
    print('Done!', end='\n\n')
    _inform(results)


def _parseArgs(font, classData, glyphnameData, fontData,
               keys, includeOptionals, overwrite) -> argparse.Namespace:
    # Define command line arguments.
    parser = argparse.ArgumentParser(
        parents=[cli.argParser(font=font,
                               classData=classData,
                               glyphnameData=glyphnameData,
                               fontData=fontData,
                               overwrite=overwrite)],
        description='Set annotation attributes from SMuFL metadata.')

    parser.add_argument(
        '-k', '--keys', type=str, default=keys,
        help=("Annotation keys to be set. Value can be either 'name' "
              "(i.e., SMuFL-specific canonical glyph name), 'classes', "
              "'description' or tuple of several."))

    parser.add_argument(
        '-o', '--include-optionals', action='store_true',
        default=includeOptionals,
        help="Include annotation for optional glyphs where available.",
        dest='includeOptionals')

    args = parser.parse_args()

    if isinstance(args.classData, Request):
        args.classData = args.classData.json()
    if isinstance(args.glyphnameData, Request):
        args.glyphnameData = args.glyphnameData.json()
    if isinstance(args.fontData, Request):
        args.fontData = args.fontData.json()
    if isinstance(args.keys, str):
        args.keys = (args.keys,)
    return args


def _buildGlyphMaps(font, keys, includeOptionals, classData,
                    glyphnameData, fontData) -> Dict[str, Dict]:
    # Build dictionary of annotation keys mapped to glyphMaps.

    def _buildGlyphMap(key, metadata) -> Dict[int, str]:
        # Build dictionary of codepoints mapped to annotation values.

        # Descriptions for ligatures are not included in
        # the 'OptionalGlyphs' section of bravura_metadata.json, and
        # lookups in both sections are therefore needed.

        glyphMap = {}
        if 'optionalGlyphs' in metadata:
            metadata = metadata['optionalGlyphs'] | metadata['ligatures']
        for name, data in metadata.items():
            try:
                codepoint = converters.toDecimal(data['codepoint'])
            except TypeError:
                codepoint = name
            if key == 'name':
                glyphMap[codepoint] = name
            else:
                glyphMap[codepoint] = data.get(key, None)
        return glyphMap

    def _buildClasses(font, classData, glyphnameData):
        # Build glyphMap for 'classes'.
        # Invert classData dictionary to codepoints mapped to classes.
        # Loop through glyph basenames to get classes for optional glyphs.
        classes = collections.defaultdict(list)
        for clas, glyphs in classData.items():
            for glyph in glyphs:
                name = converters.toUniName(glyphnameData[glyph]['codepoint'])
                classes[name].append(clas)
        return {g.rGlyph.unicode: classes[g.base.name] for g in font if g.base}

    glyphMaps = {}
    for key in keys:
        metadata = glyphnameData
        if key == 'classes':
            glyphMaps[key] = _buildClasses(font, classData, glyphnameData)
        glyphMaps[key] = _buildGlyphMap(key, metadata)
        if includeOptionals:
            glyphMaps[key] |= _buildGlyphMap(key, fontData)

    return glyphMaps


def _inform(results):
    # Print diagnostic report to console.
    print("Annotated glyphs:".upper(), end='\n\n')
    for key, glyph in results['annotated'].items():
        print(f"\t{key.title()}:")
        print(f"\t\t{sorted(glyph)}", end='\n\n')

    print("skipped glyphs:".upper(), end='\n\n')
    for category, values in results.items():
        if category == 'annotated':
            continue

        if category == 'unencoded':
            print(f"\t{category.title()}:")
            print(f"\t\t{sorted(values)}", end='\n\n')

        elif category == 'malformatted':
            print(f"\t{category.title()} "
                  f"{Glyph().__class__.__name__}.rGlyph.note:")
            print(f"\t\t{sorted(values)}", end='\n\n')

        elif category == 'lookupError':
            for key, glyph in values.items():
                print(f"\tUnsuccessful {key} lookup:")
                print(f"\t\t{sorted(glyph)}", end='\n\n')

        else:
            print(f"\t{category.title()}:")
            print(f"\t\t{sorted(values)}", end='\n\n')


if __name__ == '__main__':
    setAnnotation()
