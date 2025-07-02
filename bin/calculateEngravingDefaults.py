#!/usr/bin/env python3
"""Calculate engraving defaults from glyph contours.

This script calculates and sets attribute values for the :class:`.EngravingDefaults`
class based on glyph dimensions, registration, metrics, and point placement.

It offers options to override automatic contour measurements and reassign attributes to
different ruler functions or glyphs. Refer to :data:`.ENGRAVING_DEFAULTS_MAPPING` for a
comprehensive list of attributes and their default corresponding glyphs and assigned
ruler functions.

.. note::

    The setting for :attr:`.textFontFamily` must be set manually within the `override`
    parameter.

The script requires SMufoLib to be installed in its execution environment. It can be
used from the command line or as a Python module. See the
:ref:`calculate-engraving-defaults-cli` and :ref:`calculate-engraving-defaults-python`
sections below for usage details.

.. versionchanged:: 0.5.0

    The `referenceIndex` parameter has been removed from all ruler functions and is no
    longer needed when providing remappings.

    The ruler functions have been removed from this script and are now available in the
    :mod:`.rulers` module.

"""

from __future__ import annotations
from collections.abc import Callable
import argparse
import json
import textwrap
from pathlib import Path

from tqdm import tqdm

from smufolib import (
    Font,
    Glyph,
    cli,
    config,
    error,
    normalizers,
    stdUtils,
)
from smufolib.utils.rulers import ENGRAVING_DEFAULTS_MAPPING, DISPATCHER
from smufolib.utils.scriptUtils import normalizeFont as _normalizeFont


Exclude = tuple[str] | list[str]
OverrideValue = int | float | tuple[str, ...] | None
Override = dict[str, OverrideValue]
Remapping = dict[str, dict[str, str]]
RulerType = Callable[[Glyph], int | float | None]

CONFIG = config.load()

# Parameter defaults
EXCLUDE = None
OVERRIDE = None
SPACES = False
REMAP = None
VERBOSE = False


# pylint: disable=R0913, C0103, R0914


def calculateEngravingDefaults(
    font: Font | Path | str,
    exclude: Exclude | None = EXCLUDE,
    override: Override | None = OVERRIDE,
    remap: Remapping | None = REMAP,
    spaces: bool = SPACES,
    verbose: bool = VERBOSE,
) -> None:
    """Calculate engraving defaults from glyph contours (Python API).

    :param font: Target :class:`.Font` object or path to font file.
    :param exclude: :class:`.EngravingDefaults` attributes to exclude.
        Defaults to :obj:`None`.
    :param override: :class:`.EngravingDefaults` attributes to manually
        override mapped to their values. Defaults to :obj:`None`.
    :param remap: :class:`.EngravingDefaults` attributes mapped to
        remappings :class:`dict`, e.g.:

        .. code-block:: python

            r = {
                "arrowShaftThickness": {
                    "ruler": "glyphBoundsXMinAbs",
                    "glyph": "uniEB60"
                }
            }

        Defaults to :obj:`None`.
    :param spaces: Whether values for overrides are given in staff
        spaces instead of font units. Defaults to :obj:`False`.
    :param verbose: Make output verbose. Defaults to :obj:`False`.
    :raises TypeError: If any parameter value is not the expected type.
    :raises ValueError: If any parameter value item is not the expected
        type or value.

    """

    print("Starting...")

    font = _normalizeFont(font)
    exclude = _normalizeExclude(exclude)
    override = _normalizeOverride(override)
    remap = _normalizeRemap(remap)

    font.smufl.spaces = False

    iterator = ENGRAVING_DEFAULTS_MAPPING.items()
    if not verbose:
        iterator = tqdm(ENGRAVING_DEFAULTS_MAPPING.items())

    stdUtils.verbosePrint("\nSetting attributes:", verbose)
    for key, mapping in iterator:
        if exclude and key in exclude:
            continue

        if key == "textFontFamily":
            if override and key in override:
                value = override[key]
                setattr(font.smufl.engravingDefaults, key, value)
                stdUtils.verbosePrint(f"\t'{key}': {value}", verbose)
            continue

        rulerName = mapping.get("ruler", "")
        glyphName = mapping.get("glyph", "")
        remapping = remap.get(key, {}) if remap else {}
        rulerName = remapping.get("ruler", rulerName)
        ruler: RulerType = DISPATCHER[rulerName]
        glyphName = remapping.get("glyph", glyphName)

        rulerValue = _getValue(
            font=font,
            key=key,
            glyphName=glyphName,
            ruler=ruler,
            verbose=verbose,
        )
        if rulerValue is None:
            continue

        if override and key in override:
            value = override[key]
        else:
            value = rulerValue
        if spaces and isinstance(value, (int, float)):
            value = font.smufl.toUnits(value)

        setattr(font.smufl.engravingDefaults, key, value)
        if spaces and value and isinstance(value, (int, float)):
            value = font.smufl.toSpaces(value)
        stdUtils.verbosePrint(f"\t'{key}': {value}", verbose)
    stdUtils.verbosePrint("\nSaving font...", verbose)
    font.save()
    print("\nDone!")


def main() -> None:
    """Command line entry point."""
    args = _parseArgs()
    calculateEngravingDefaults(
        args.font,
        exclude=args.exclude,
        override=args.override,
        remap=args.remap,
        spaces=args.spaces,
        verbose=args.verbose,
    )


# -------
# Helpers
# -------


def _normalizeExclude(exclude: Exclude | None) -> Exclude | None:
    # Noralize `exclude`.
    if exclude is None:
        return None

    error.validateType(exclude, (tuple, list), "exclude")

    for item in exclude:
        error.suggestValue(
            item, list(ENGRAVING_DEFAULTS_MAPPING.keys()), "exclude", items=True
        )
    return exclude


def _normalizeOverride(override: Override | None) -> Override | None:
    # Normalize override dictionary.
    if override is None:
        return None

    error.validateType(override, dict, "override")
    for key, value in override.items():
        attributes = list(ENGRAVING_DEFAULTS_MAPPING.keys())
        error.suggestValue(key, attributes, "override", items=True)
        normalizers.normalizeEngravingDefaultsAttr(key, value)

    return override


def _normalizeRemap(remap: Remapping | None) -> Remapping | None:
    # Normalize remap dictionary.
    if remap is None:
        return None

    error.validateType(remap, dict, "remap")

    for key, value in remap.items():
        error.suggestValue(
            key, list(ENGRAVING_DEFAULTS_MAPPING.keys()), "remap", items=True
        )

        for k, v in value.items():
            error.suggestValue(
                k,
                ("ruler", "glyph"),
                f"'remap'['{value}']",
                items=True,
            )

            error.validateType(
                v, (str, int, type(None)), f"'remap'['{value}']", items=True
            )

    return remap


def _getValue(
    font: Font,
    key: str,
    glyphName: str,
    ruler: RulerType,
    verbose: bool,
) -> int | float | None:
    # Get value from ruler function and print error message.
    try:
        glyph = font[glyphName]
        return ruler(glyph)
    except KeyError:
        stdUtils.verbosePrint(
            "Skipping attribute assigned to non-"
            f"existent glyph: '{key}' ('{glyphName}')",
            verbose,
        )
        return None


def _parseArgs() -> argparse.Namespace:
    # Parse command line arguments and options.
    parser = argparse.ArgumentParser(
        description=stdUtils.getSummary(__doc__),
        parents=[
            cli.commonParser(
                "font", exclude=EXCLUDE, spaces=SPACES, verbose=VERBOSE, addHelp=False
            )
        ],
        formatter_class=cli.createHelpFormatter(
            ("ArgumentDefaultsHelpFormatter", "RawDescriptionHelpFormatter")
        ),
    )

    parser.add_argument(
        "-o",
        "--override",
        default=OVERRIDE,
        type=json.loads,
        help=textwrap.dedent(
            """JSON string of attributes and values to manually override
            in the format: '{"<attributeName>": <value>, ...}'"""
        ),
    )

    parser.add_argument(
        "-r",
        "--remap",
        default=REMAP,
        type=json.loads,
        help=textwrap.dedent(
            """JSON string of ruler and glyph remappings
            in the format: '{"<attributeName>": {"ruler": "<functionName>", 
            "glyph": "<glyphName>"}, ...}'"""
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
