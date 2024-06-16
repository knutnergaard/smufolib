#!/usr/bin/env python3
# coding: utf-8
"""
This script deletes SMuFL-specific metadata and glyph anchors from a UFO
font file.

To prevent unwanted data loss, items to delete *must* be specifically
included and may also be specifically exlcuded. If ``exclude='None'``,
``include='*'`` (all) will delete everything, essentially resetting the
font to a Non-SMuFL state. Individual attribute and anchor names may
otherwise be specified in both parameters as a single string or tuple
of any of the following values:

    Attributes
        ``'designSize'``
        ``'sizeRange'``
        ``'engravingDefaults'``
        ``'name'``
        ``'classes'``
        ``'description'``
        ``'spaces'``

    Anchors
        ``'splitStemUpSE'``
        ``'splitStemUpSW'``
        ``'splitStemDownNE'``
        ``'splitStemDownNW'``
        ``'stemUpSE'``
        ``'stemDownNW'``
        ``'stemUpNW'``
        ``'stemDownSW'``
        ``'nominalWidth'``
        ``'numeralTop'``
        ``'numeralBottom'``
        ``'cutOutNE'``
        ``'cutOutSE'``
        ``'cutOutSW'``
        ``'cutOutNW'``
        ``'graceNoteSlashSW'``
        ``'graceNoteSlashNE'``
        ``'graceNoteSlashNW'``
        ``'graceNoteSlashSE'``
        ``'repeatOffset'``
        ``'noteheadOrigin'``
        ``'opticalCenter'``

.. Warning:: This script will permanently delete data. Remember to
   always back up your file before running.

This script requires that SMufoLib be installed within its executive
environment. It may also be imported as a module and contains the
following public funcitons:

    * :func:`importID` – The scripts program function.
    * :func:`main` - Command line entry point.

"""
from collections.abc import Iterable
import argparse
from pathlib import Path

from tqdm import tqdm

from smufolib import Font, cli
from smufolib.constants import (
    ANCHOR_NAMES, FONT_ATTRIBUTES, GLYPH_ATTRIBUTES)

# Parameter defaults
EXCLUDE = None
VERBOSE = False

# pylint: disable=C0103


def cleanFont(font: Font | Path | str,
              include: Iterable,
              exclude: Iterable = EXCLUDE,
              verbose: bool = VERBOSE):
    """Delete :class:`~smufolib.smufl.Smufl` class attribute values.

    :param font: Object or path to
     target :class:`~smufolib.objects.font.Font`.
    :param include: items to be deleted. May be ``'*'`` (all), an
     individual attribute or anchor name as a :class:`str`
     or :class:`tuple` of several.
    :param exclude: Items to be preserved if `ìnclude='*'``. Defaults to
     ``None``.
    :param verbose: Make output verbose. Defaults to ``False``.

    """
    print("Processing...", end="\n\n")

    # Convert font path to object.
    font = font if isinstance(font, Font) else Font(font)

    # Define print function to be do-nothing if verbose=False.
    verboseprint = print if verbose else lambda *a, **k: None

    itemsToClean = _buildItemsDict(include, exclude)

    # Clean font attributes
    print("Cleaning font attributes...", end="\n\n")
    for attr in itemsToClean['fontAttributes']:
        if attr == 'engravingDefaults':
            font.smufl.engravingDefaults.clear()
        elif attr == 'spaces':
            setattr(font.smufl, attr, False)
        else:
            setattr(font.smufl, attr, None)

    print("Cleaning glyph items...")
    for glyph in font if verbose else tqdm(font):
        # Clean glyph attributes
        for index, attr in enumerate(itemsToClean['glyphAttributes']):
            if not getattr(glyph.smufl, attr):
                continue
            if index == 0:
                verboseprint("\nCleaning attributes from glyph:", glyph)
            setattr(glyph.smufl, attr, None)
            verboseprint(f"\t{attr}")

        # Clean Anchors
        if not any(a in itemsToClean['anchors'] for a in glyph.anchors):
            continue
        for anchor in glyph.anchors:
            if not anchor or anchor.name not in itemsToClean['anchors']:
                continue
            if anchor.index == 0:
                verboseprint("\nCleaning anchors from glyph:", glyph)
            glyph.removeAnchor(anchor.index)
            verboseprint(f"\t{anchor.name}")

    font.save()
    print("\nDone!")


def main():
    """Command line entry point."""
    args = _parseArgs()
    cleanFont(args.font,
              args.include,
              exclude=args.exclude,
              verbose=args.verbose)


def _buildItemsDict(include, exclude):
    # Build dict of attribute and anchor items to remove.

    itemsToClean = {}
    itemsToClean['fontAttributes'] = []
    itemsToClean['glyphAttributes'] = []
    itemsToClean['anchors'] = []

    if include == '*':
        include = FONT_ATTRIBUTES | GLYPH_ATTRIBUTES | ANCHOR_NAMES
    include = (include,) if isinstance(include, str) else include

    exclude = () if exclude is None else exclude
    exclude = (exclude,) if isinstance(exclude, str) else exclude

    for item in include:
        if item in exclude:
            continue
        if item in FONT_ATTRIBUTES:
            itemsToClean['fontAttributes'].append(item)
        elif item in GLYPH_ATTRIBUTES:
            itemsToClean['glyphAttributes'].append(item)
        elif item in ANCHOR_NAMES:
            itemsToClean['anchors'].append(item)
        else:
            raise ValueError(f"Invalid item: '{item}'.")

    return itemsToClean


def _parseArgs() -> argparse.Namespace:
    # Parse command line arguments and options.
    parser = argparse.ArgumentParser(
        parents=[cli.commonParser(
            'font',
            'include',
            exclude=EXCLUDE,
            verbose=VERBOSE)],
        description='Set annotation include from SMuFL metadata.')
    return parser.parse_args()


if __name__ == '__main__':
    main()
