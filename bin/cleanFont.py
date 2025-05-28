#!/usr/bin/env python3
"""Remove SMuFL font data.

.. warning::

    This script will permanently delete data. Always back up your font file before use.

This script deletes SMuFL-specific metadata and glyph anchors from a UFO font file.

The following attribute and anchor names may be specified for inclusion or exclusion:

    Attributes
        - `designSize`
        - `sizeRange`
        - `engravingDefaults`
        - `name`
        - `classes`
        - `description`
        - `spaces`

    Anchors
        - `splitStemUpSE`
        - `splitStemUpSW`
        - `splitStemDownNE`
        - `splitStemDownNW`
        - `stemUpSE`
        - `stemDownNW`
        - `stemUpNW`
        - `stemDownSW`
        - `nominalWidth`
        - `numeralTop`
        - `numeralBottom`
        - `cutOutNE`
        - `cutOutSE`
        - `cutOutSW`
        - `cutOutNW`
        - `graceNoteSlashSW`
        - `graceNoteSlashNE`
        - `graceNoteSlashNW`
        - `graceNoteSlashSE`
        - `repeatOffset`
        - `noteheadOrigin`
        - `opticalCenter`

The script requires SMufoLib to be installed in its execution environment. It can be
used from the command line or as a Python module. See the :ref:`clean-font-cli` and
:ref:`clean-font-python` sections below for usage details.

"""

from collections.abc import Iterable
import argparse
from pathlib import Path

from tqdm import tqdm

from smufolib import Font
from smufolib.objects.smufl import ANCHOR_NAMES, FONT_ATTRIBUTES, GLYPH_ATTRIBUTES
from smufolib.cli import REQUIRED, commonParser
from smufolib.utils import error, stdUtils
from smufolib.utils.scriptUtils import normalizeFont as _normalizeFont


# Parameter defaults
EXCLUDE = None
VERBOSE = False

# pylint: disable=C0103


def cleanFont(
    font: Font | Path | str,
    include: Iterable,
    exclude: Iterable | None = EXCLUDE,
    verbose: bool = VERBOSE,
):
    """Delete Smufl-specific attribute values (Python API).

    Use the `include` and `exclude` keyword arguments to control which attributes and
    anchors are removed.

    To avoid unintentional data loss, `include` must be specified. Setting `include="*"`
    will delete all SMuFL metadata and anchors.

    Refer to the list of valid keys in the main docstring.

    :param font: Target :class:`.Font` object or path to font file.
    :param include: Items to be deleted. May be ``"*"`` (all), an individual attribute
        or anchor name as a :class:`str` or :class:`tuple` of several.
    :param exclude: Items to be preserved if ``ìnclude="*"``. Defaults to :obj:`None`.
    :param verbose: Make output verbose. Defaults to :obj:`False`.
    :raises TypeError: If any parameter value is not the expected type.
    :raises ValueError: If any item in `include` or `exclude` is invalid.

    """
    print("Starting...")

    font = _normalizeFont(font)
    itemsToClean = _buildItemsDict(include, exclude)

    # Clean font attributes
    stdUtils.verbosePrint("\nCleaning attributes for font:", verbose)
    for attr in itemsToClean["fontAttributes"]:
        if font.smufl.engravingDefaults and attr == "engravingDefaults":
            font.smufl.engravingDefaults.clear()
        elif attr == "spaces":
            setattr(font.smufl, attr, False)
        else:
            setattr(font.smufl, attr, None)
        stdUtils.verbosePrint(f"\t'{attr}'", verbose)

    for glyph in font if verbose else tqdm(font):
        # Clean glyph attributes
        glyphAttributesCleaned = False
        for attr in itemsToClean["glyphAttributes"]:
            if not getattr(glyph.smufl, attr):
                continue

            if not glyphAttributesCleaned:
                stdUtils.verbosePrint(
                    f"\nCleaning attributes from glyph '{glyph.name}':", verbose
                )
                glyphAttributesCleaned = True

            setattr(glyph.smufl, attr, None)
            stdUtils.verbosePrint(f"\t'{attr}'", verbose)

        # Clean Anchors
        anchorsCleaned = False
        for anchor in glyph.anchors:
            if anchor.name not in itemsToClean["anchors"]:
                continue

            if not anchorsCleaned:
                stdUtils.verbosePrint(
                    f"\nCleaning anchors from glyph '{glyph.name}':", verbose
                )
                anchorsCleaned = True

            glyph.removeAnchor(anchor.index)
            stdUtils.verbosePrint(f"\t'{anchor.name}'", verbose)

    stdUtils.verbosePrint("\nSaving font...", verbose)
    font.save()

    print("\nDone.")


def main() -> None:
    """Command line entry point."""
    args = _parseArgs()
    cleanFont(args.font, args.include, exclude=args.exclude, verbose=args.verbose)


def _buildItemsDict(include, exclude):
    # Build dict of attribute and anchor items to remove.

    itemsToClean = {"fontAttributes": [], "glyphAttributes": [], "anchors": []}

    allItems = FONT_ATTRIBUTES | GLYPH_ATTRIBUTES | ANCHOR_NAMES
    exclude = () if exclude is None else exclude
    exclude = (exclude,) if isinstance(exclude, str) else exclude

    for item in exclude:
        error.suggestValue(item, allItems, "exclude")

    if include in ("*", ["*"]):
        include = allItems
    elif isinstance(include, str):
        include = (include,)

    for item in include:
        if item in exclude:
            continue

        if item in FONT_ATTRIBUTES:
            itemsToClean["fontAttributes"].append(item)
        elif item in GLYPH_ATTRIBUTES:
            itemsToClean["glyphAttributes"].append(item)
        elif item in ANCHOR_NAMES:
            itemsToClean["anchors"].append(item)
        else:
            error.suggestValue(item, allItems, "include")

    return itemsToClean


def _parseArgs() -> argparse.Namespace:
    # Parse command line arguments and options.
    parser = commonParser(
        "font",
        include=REQUIRED,
        description=stdUtils.getSummary(__doc__),
        exclude=EXCLUDE,
        verbose=VERBOSE,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
