#!/usr/bin/env python3
# coding: utf-8
"""
This script imports :class:`~smufolib.objects.smufl.Smufl`
identification attribute values for all glyphs in a SMufoLib
:class:`~smufolib.objects.font.Font` from metadata files. More
specifically, it automatically sets the values for
:attr:`~smufolib.objects.smufl.Smufl.name`,
:attr:`~smufolib.objects.smufl.Smufl.description` and/or
:attr:`~smufolib.objects.smufl.Smufl.classes`, based on the official metadata
files of `SMuFL <https://w3c.github.io/smufl/latest/specification/smufl-metadata.html>`_
and `Bravura <https://github.com/steinbergmedia/bravura#bravura-music-font>`_,
or any other compatible sources.

Attributes for optional glyphs may be included with `includeOptionals`
is :obj:`True`, in which case stylistic alternates and ligatures must
be named with reference to their base glyph(see :ref:`this note <about
glyph naming>` for more information about glyph naming).

If `overwrite` is :obj:`False`, glyphs with preset attributes are
skipped. Glyphs are also skipped if they are non-SMuFL members or if
lookup fails (because the glyph is unencoded or the codepoint does not
exist in the source metadata.

This script requires SMufoLib to be installed within its
executive environment. It may also be imported as a module and contains
the following public functions:

    - :func:`importID` – The scripts program function.
    - :func:`main` - Command line entry point.

"""

from __future__ import annotations
from typing import Any
import argparse
import collections
from contextlib import nullcontext
from pathlib import Path
import time

from tqdm import tqdm

from smufolib import (
    Font,
    Request,
    cli,
    config,
    converters,
    error,
    stdUtils,
)
from smufolib.utils.scriptUtils import normalizeFont as _normalizeFont
from smufolib.utils.scriptUtils import normalizeJsonDict as _normalizeJsonDict
from smufolib.utils.scriptUtils import normalizeRequest as _normalizeRequest

# Type aliases
JsonDict = dict[str, Any]
GlyphMap = dict[int, str | list[str]]
AttributesMap = dict[str, GlyphMap]

# Configuration
CONFIG = config.load()

# Parameter defaults
CLASSES_DATA = Request(
    CONFIG["metadata.paths"]["classes"], CONFIG["metadata.fallbacks"]["classes"]
)
GLYPHNAMES_DATA = Request(
    CONFIG["metadata.paths"]["glyphnames"], CONFIG["metadata.fallbacks"]["glyphnames"]
)
FONT_DATA = Request(
    CONFIG["metadata.paths"]["referenceFont"],
    CONFIG["metadata.fallbacks"]["referenceFont"],
)
ATTRIBUTES = ("name", "classes", "description")
INCLUDE_OPTIONALS = False
OVERWRITE = False
VERBOSE = False

# pylint: disable=R0913, R0914, C0103


def importID(
    font: Font | Path | str,
    attributes: str | tuple[str, ...] = "*",
    classesData: Request | Path | str = CLASSES_DATA,
    glyphnamesData: Request | Path | str = GLYPHNAMES_DATA,
    fontData: Request | Path | str = FONT_DATA,
    includeOptionals: bool = INCLUDE_OPTIONALS,
    overwrite: bool = OVERWRITE,
    verbose: bool = VERBOSE,
) -> None:
    """Import SMuFL identification attributes.

    :param font: Object or path to target :class:`.Font`.
    :param attributes: ID attributes to be set. Value can be either
        ``'*'`` (all), ``'name'``, ``'classes'``, ``'description'``)
        or :class:`tuple` of several. Defaults to ``'*'``.
    :param classesData: Object call or direct path to classes metadata
        file. Defaults to :class:`.Request` with :attr:`~.Request.path`
        and :attr:`~.Request.fallback` set to
        :ref:`[metadata.paths]` and :ref:`[metadata.fallbacks]`
        respective `classes` configurations.
    :param glyphnamesData: Object call or direct path to glyphnames
        metadata file. Defaults to :class:`~.Request`
        with :attr:`~.Request.path` and :attr:`~.Request.fallback` set
        to :ref:`[metadata.paths]` and :ref:`[metadata.fallbacks]`
        respective `glyphnames` configurations.
    :param fontData: Object call or direct path to reference font
        metadata file. Defaults to :class:`~.Request`
        with :attr:`~.Request.path` and :attr:`~.Request.fallback` set
        to :ref:`[metadata.paths]` and :ref:`[metadata.fallbacks]`
        respective `referenceFont` configurations.
    :param includeOptionals: Include optional glyphs. Defaults to
        :obj:`False`.
    :param overwrite: Overwrite preexisting values. Defaults to
        :obj:`False`.
    :param verbose: Make output verbose. Defaults to :obj:`False`.
    :raises TypeError: If any parameter value is not the expected type.
    :raises ValueError: If `attributes` value is not a valid ID
        attribute.

    """
    print("Starting...")

    font = _normalizeFont(font)
    ticks = len(font) * 2 + 2
    with tqdm(total=ticks) if not verbose else nullcontext() as progressBar:
        attributes = _normalizeAttributes(attributes)
        classesDataJson = _normalizeJsonDict(_normalizeRequest(classesData).json())
        glyphnamesDataJson = _normalizeJsonDict(
            _normalizeRequest(glyphnamesData).json()
        )
        fontDataJson = _normalizeJsonDict(_normalizeRequest(fontData).json())

        if progressBar:
            progressBar.update(1)
            time.sleep(0.0001)

        stdUtils.verbosePrint("\nBuilding glyphmaps...", verbose)
        glyphMaps = _buildAttributesMap(
            font=font,
            attributes=attributes,
            includeOptionals=includeOptionals,
            classesDataJson=classesDataJson,
            glyphnamesDataJson=glyphnamesDataJson,
            fontDataJson=fontDataJson,
            progressBar=progressBar,
        )

        for glyph in font:
            if progressBar:
                progressBar.update(1)
                time.sleep(0.0001)

            codepoint = glyph.unicode
            if not codepoint:
                stdUtils.verbosePrint(
                    f"\nSkipping unencoded glyph: '{glyph.name}'", verbose
                )
                continue

            if not glyph.smufl.isMember:
                stdUtils.verbosePrint(
                    f"\nSkipping non-SMuFL glyph: '{glyph.name}'", verbose
                )
                continue

            if glyph.smufl.isOptional and not includeOptionals:
                stdUtils.verbosePrint(
                    f"\nSkipping optional glyph: '{glyph.name}'", verbose
                )
                continue

            stdUtils.verbosePrint(
                f"\nSetting attributes for glyph '{glyph.name}':", verbose
            )
            for attribute in attributes:
                if codepoint not in glyphMaps[attribute]:
                    stdUtils.verbosePrint(f"\t'{attribute}': not found", verbose)
                    continue

                if getattr(glyph.smufl, attribute) and not overwrite:
                    stdUtils.verbosePrint(f"\t'{attribute}': preset", verbose)
                    continue

                setattr(glyph.smufl, attribute, glyphMaps[attribute][codepoint])
                stdUtils.verbosePrint(f"\t'{attribute}': set", verbose)

        stdUtils.verbosePrint("\nSaving font...", verbose)
        font.save()
        if progressBar:
            progressBar.update(1)
            time.sleep(0.0001)

    print("\nDone.")


def main() -> None:
    """Command line entry point."""
    args = _parseArgs()
    importID(
        args.font,
        args.attributes,
        classesData=args.classesData,
        glyphnamesData=args.glyphnamesData,
        fontData=args.fontData,
        includeOptionals=args.includeOptionals,
        overwrite=args.overwrite,
        verbose=args.verbose,
    )


def _normalizeAttributes(value: str | tuple[str, ...]) -> tuple[str, ...]:
    # Normalize values in the ``attributes`` parameter.

    value = ATTRIBUTES if value == "*" else value
    value = (value,) if isinstance(value, str) else value
    error.validateType(value, (str, tuple), "attributes")
    for val in value:
        if val not in ATTRIBUTES:
            error.suggestValue(val, ATTRIBUTES, "attributes", items=True)
    return value


def _buildAttributesMap(
    font: Font,
    attributes: str | tuple[str, ...],
    includeOptionals: bool,
    classesDataJson: JsonDict,
    glyphnamesDataJson: JsonDict,
    fontDataJson: JsonDict,
    progressBar: tqdm,
) -> AttributesMap:
    # Build dictionary of ID attributes mapped to glyph maps.

    def _buildGlyphMap(attribute: str, metadata: JsonDict) -> GlyphMap:
        # Build dictionary of codepoints mapped to attribute values.

        # Descriptions for ligatures are not included in
        # the 'OptionalGlyphs' section of bravura_metadata.json, and
        # lookups in both sections are therefore needed.

        glyphMap: GlyphMap = {}
        if "optionalGlyphs" in metadata:
            metadata = metadata["optionalGlyphs"] | metadata["ligatures"]
        for name, data in metadata.items():
            codepoint = converters.toDecimal(data["codepoint"])
            if attribute == "name":
                glyphMap[codepoint] = name
            else:
                glyphMap[codepoint] = data.get(attribute, None)

        return glyphMap

    def _buildClassMap(
        font: Font, classesDataJson: JsonDict, glyphnamesDataJson: JsonDict
    ) -> GlyphMap:
        # Build glyph map for 'classes'.

        # GlyphnamesData has a number of unused codepoints and
        # codepoints for text based fonts (58 as of this writing) which
        # should be skipped.

        # Invert classesData dictionary to glyph names mapped to classes.
        classMap: GlyphMap = {}
        classes = collections.defaultdict(list)
        for clas, glyphs in classesDataJson.items():
            for glyph in glyphs:
                name = converters.toUniName(glyphnamesDataJson[glyph]["codepoint"])
                classes[name].append(clas)

        # Loop through basenames to get classes for optional glyphs and
        # index on codepoints.
        for glyph in font:
            if progressBar:
                progressBar.update(1)
                time.sleep(0.0001)
            if not glyph.smufl.codepoint or not glyph.smufl.base:
                continue
            if glyph.smufl.base.name not in classes:
                continue
            if includeOptionals or not glyph.smufl.isOptional:
                classMap[glyph.unicode] = classes[glyph.smufl.base.name]

        return classMap

    glyphMaps: AttributesMap = {}
    for attribute in attributes:
        if attribute == "classes":
            glyphMaps[attribute] = _buildClassMap(
                font=font,
                classesDataJson=classesDataJson,
                glyphnamesDataJson=glyphnamesDataJson,
            )
        else:
            glyphMaps[attribute] = _buildGlyphMap(
                attribute=attribute, metadata=glyphnamesDataJson
            )
            if includeOptionals:
                glyphMaps[attribute] |= _buildGlyphMap(
                    attribute=attribute, metadata=fontDataJson
                )

    return glyphMaps


def _parseArgs() -> argparse.Namespace:
    # Parse command line arguments and options.
    parser = cli.commonParser(
        "font",
        description=stdUtils.getSummary(importID.__doc__),
        attributes="*",
        classesData=CLASSES_DATA,
        glyphnamesData=GLYPHNAMES_DATA,
        fontData=FONT_DATA,
        includeOptionals=INCLUDE_OPTIONALS,
        overwrite=OVERWRITE,
        verbose=VERBOSE,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
