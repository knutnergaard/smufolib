#!/usr/bin/env python3
# coding: utf-8

"""This script imports :class:`~smufolib.objects.smufl.Smufl`
identification attribute values for all the glyphs in a SMufoLib
:class:`~smufolib.objects.font.Font` from metadata files. More
specifically, it automatically sets the values for
:attr:`~smufolib.objects.smufl.Smufl.name`,
:attr:`~smufolib.objects.smufl.Smufl.description` and/or
:attr:`~smufolib.objects.smufl.Smufl.classes`, based on the official metadata
files of `SMuFL <https://w3c.github.io/smufl/latest/specification/smufl-metadata.html>`_
and `Bravura <https://github.com/steinbergmedia/bravura#bravura-music-font>`_,
or any other compatible sources.

If ``includeOptionals=True``, optional alternates and ligatures
require that such glyphs be named with reference to their base glyph
(see :ref:`this note <about glyph naming>` for more information about
glyph naming).

If ``overwrite=False``, glyphs with preset attributes are skipped.
Glyphs are also skipped if they are non-SMuFL members or if lookup
fails (because the glyph is unencoded or the codepoint does not exist
in the source metadata.

This script requires that SMufoLib be installed within its
executive environment. It may also be imported as a module and contains
the following public functions:

    * :func:`importID` – The scripts program function.
    * :func:`main` - Command line entry point.

"""
from __future__ import annotations
import argparse
import collections
from pathlib import Path

from tqdm import tqdm

from smufolib import Font, Request, cli, config, converters

CONFIG = config.load()

# Parameter defaults
CLASSES_DATA = Request(CONFIG['metadata.paths']['classes'],
                       CONFIG['metadata.fallbacks']['classes'])
GLYPHNAMES_DATA = Request(CONFIG['metadata.paths']['glyphnames'],
                          CONFIG['metadata.fallbacks']['glyphnames'])
FONT_DATA = Request(CONFIG['metadata.paths']['referenceFont'],
                    CONFIG['metadata.fallbacks']['referenceFont'])
ID_ATTRIBUTES = ('name', 'classes', 'description')
INCLUDE_OPTIONALS = False
OVERWRITE = False
VERBOSE = False


# pylint: disable=R0913, R0914, C0103


def importID(font: Font | Path | str,
             attributes: str | tuple[str, ...] = ID_ATTRIBUTES,
             classesData: Request | Path | str = CLASSES_DATA,
             glyphnamesData: Request | Path | str = GLYPHNAMES_DATA,
             fontData: Request | Path | str = FONT_DATA,
             includeOptionals: bool = INCLUDE_OPTIONALS,
             overwrite: bool = OVERWRITE,
             verbose: bool = VERBOSE
             ) -> None:
    """Import SMuFL identification attributes.

    :param font: Object or path to target :class:`~smufolib.Font`.
    :param attributes: ID attributes to be set. Value can be either
     ``'name'``, ``'classes'``, ``'description'`` or :class:`tuple` of
     several. Defaults to all.
    :param classesData: Object call or direct path to classes metadata
     file. Defaults to :class:`~smufolib.request.Request`
     with :attr:`~smufolib.request.Request.path`
     and :attr:`~smufolib.request.Request.fallback` set to
     :ref:`[metadata.paths]` and :ref:`[metadata.fallbacks]` respective
     ``classes`` configurations.
    :param glyphnamesData: Object call or direct path to glyphnames
     metadata file. Defaults
     to :class:`~smufolib.request.request.Request`
     with :attr:`~smufolib.request.Request.path`
     and :attr:`~smufolib.request.Request.fallback` set to
     :ref:`[metadata.paths]` and :ref:`[metadata.fallbacks]` respective
     ``glyphnames`` configurations.
    :param fontData: Object call or direct path to reference font
     metadata file. Defaults to :class:`~smufolib.request.Request`
     with :attr:`~smufolib.request.Request.path`
     and :attr:`~smufolib.request.Request.fallback` set to
     :ref:`[metadata.paths]` and :ref:`[metadata.fallbacks]` respective
     ``referenceFont`` configurations.
    :param includeOptionals: Include optional glyphs. Defaults to
     ``False``.
    :param overwrite: Overwrite preexisting values. Defaults to
     ``False``.
    :param verbose: Make output verbose. Defaults to ``False``.
    :raises TypeError: if any ``attributes`` value is not of the
     accepted type.
    :raises ValueError: if ``attributes`` value is not a valid ID
     attribute.

    """
    print("Processing...", end="\n\n")

    # Convert font path to object.
    font = font if isinstance(font, Font) else Font(font)

    # Define print function to be do-nothing if verbose=False.
    verboseprint = print if verbose else lambda *a, **k: None

    attributes = _normalizeAttributes(attributes)

    try:
        classesDataJson = classesData.json()
        glyphnamesDataJson = glyphnamesData.json()
        fontDataJson = fontData.json()
    except AttributeError:
        classesDataJson = Request(classesData).json()
        glyphnamesDataJson = Request(glyphnamesData).json()
        fontDataJson = Request(fontData).json()

    print("Building glyphmaps...")
    glyphMaps = _buildGlyphMaps(font, attributes,
                                includeOptionals, classesDataJson,
                                glyphnamesDataJson, fontDataJson)

    print("\n\nSetting attributes...")
    # Use tqdm only when verbose=False.
    for glyph in font if verbose else tqdm(font):
        codepoint = glyph.unicode
        if not codepoint:
            verboseprint("Skipping unencoded glyph:", glyph)
            continue
        if not glyph.smufl.isMember:
            continue
        if glyph.smufl.isOptional and not includeOptionals:
            continue

        for attribute in attributes:
            if codepoint not in glyphMaps[attribute]:
                verboseprint(f"Unable to lookup {attribute} for glyph:", glyph)
                continue

            if (getattr(glyph.smufl, attribute) is not None and not overwrite):
                continue
            setattr(glyph.smufl, attribute, glyphMaps[attribute][codepoint])
            verboseprint(f"Setting {attribute} for glyph:", glyph)

    font.save()
    print('Done!')


def main():
    """Command line entry point."""
    args = _parseArgs()
    importID(args.font,
             args.attributes,
             classesData=args.classesData,
             glyphnamesData=args.glyphnamesData,
             fontData=args.fontData,
             includeOptionals=args.includeOptionals,
             overwrite=args.overwrite,
             verbose=args.verbose)


def _normalizeAttributes(value: str | tuple[str, ...] | list[str]):
    # Normalize values in the ``attributes`` parameter.

    if isinstance(value, str):
        value = (value,)
    try:
        for val in value:
            if val not in ID_ATTRIBUTES:
                raise ValueError("Attribute names must be 'name', 'classes' "
                                 f"or 'description', not '{val}'.")
        return value
    except TypeError as exc:
        raise TypeError("Attributes must be string or tuple of strings, "
                        f"not {type(value.__name__)}") from exc


def _buildGlyphMaps(font, attributes, includeOptionals, classesDataJson,
                    glyphnamesDataJson, fontDataJson) -> dict[str, dict]:
    # Build dictionary of ID attributes mapped to glyphMaps.

    def _buildGlyphMap(attribute, metadata) -> dict[int, str]:
        # Build dictionary of codepoints mapped to annotation values.

        # Descriptions for ligatures are not included in
        # the 'OptionalGlyphs' section of bravura_metadata.json, and
        # lookups in both sections are therefore needed.

        glyphMap = {}
        if 'optionalGlyphs' in metadata:
            metadata = metadata['optionalGlyphs'] | metadata['ligatures']
        for name, data in metadata.items():
            codepoint = converters.toDecimal(data['codepoint'])
            if attribute == 'name':
                glyphMap[codepoint] = name
            else:
                glyphMap[codepoint] = data.get(attribute, None)
        return glyphMap

    def _buildClassMap(font, classesDataJson, glyphnamesDataJson
                       ) -> dict[int, list[str]]:
        # Build glyphMap for 'classes'.

        # GlyphnamesData has a number of unused codepoints and
        # codepoints for text based fonts (58 as of this writing) which
        # should be skipped.

        # Invert classesData dictionary to glyph names mapped to classes.
        classes = collections.defaultdict(list)
        for clas, glyphs in classesDataJson.items():
            for glyph in glyphs:
                name = converters.toUniName(
                    glyphnamesDataJson[glyph]['codepoint'])
                classes[name].append(clas)

        # Loop through basenames to get classes for optional glyphs and
        # index on codepoints.
        classMap = {}
        for glyph in tqdm(font):
            if not glyph.smufl.codepoint or not glyph.smufl.base:
                continue
            if glyph.smufl.base.name not in classes:
                continue
            if includeOptionals:
                classMap[glyph.unicode] = classes[glyph.smufl.base.name]
            elif not glyph.smufl.isOptional:
                classMap[glyph.unicode] = classes[glyph.smufl.base.name]
        return classMap

    glyphMaps = {}
    for attribute in attributes:
        glyphMaps[attribute] = _buildGlyphMap(attribute, glyphnamesDataJson)
        if includeOptionals:
            glyphMaps[attribute] |= _buildGlyphMap(attribute, fontDataJson)
        if attribute == 'classes':
            glyphMaps[attribute] = _buildClassMap(
                font, classesDataJson, glyphnamesDataJson)
    return glyphMaps


def _parseArgs() -> argparse.Namespace:
    # Parse command line arguments and options.

    parser = argparse.ArgumentParser(
        parents=[cli.commonParser(
            'font',
            attributes=ID_ATTRIBUTES,
            classesData=CLASSES_DATA,
            glyphnamesData=GLYPHNAMES_DATA,
            fontData=FONT_DATA,
            includeOptionals=INCLUDE_OPTIONALS,
            overwrite=OVERWRITE,
            verbose=VERBOSE)],
        description='Set annotation attributes from SMuFL metadata.')

    return parser.parse_args()


if __name__ == '__main__':
    main()
