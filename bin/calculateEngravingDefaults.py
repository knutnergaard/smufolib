#!/usr/bin python3
# coding: utf-8

"""
This script calculates and sets attribute values for
the :class:`.EngravingDefaults` class based on glyph dimensions,
registration, metrics, and point placement.

The script provides options to override automatic contour measurements
and reassign attributes to different ruler functions or glyphs. It aims
to automate the process, but due to limitations in parameter
identification and control, it should only be used as a starting point.

By default, attributes are mapped to the following functions and
glyphs:

    ===================================   ====================   ===========
    Attribute                             Function               Glyph
    ===================================   ====================   ===========
    :attr:`.arrowShaftThickness`          :func:`xOrigin`        `uniEB60`
    :attr:`.barlineSeparation`            :func:`xInner`         `uniE031`
    :attr:`.beamSpacing`                  :func:`yInner`         `uniE1F9`
    :attr:`.beamThickness`                :func:`boundsHeight`   `uniE1F7`
    :attr:`.bracketThickness`             :func:`xOrigin`        `uniE003`
    :attr:`.dashedBarlineDashLength`      :func:`yMinimum`       `uniE036`
    :attr:`.dashedBarlineGapLength`       :func:`yInner`         `uniE036`
    :attr:`.dashedBarlineThickness`       :func:`xOrigin`        `uniE036`
    :attr:`.hairpinThickness`             :func:`yMinimum`       `uniE53E`
    :attr:`.hBarThickness`                :func:`yMinimum`       `uniE4F0`
    :attr:`.legerLineExtension`           :func:`boundsLeft`     `uniE022`
    :attr:`.legerLineThickness`           :func:`boundsHeight`   `uniE022`
    :attr:`.lyricLineThickness`           :func:`boundsHeight`   `uniE010`
    :attr:`.octaveLineThickness`          :func:`boundsHeight`   `uniE010`
    :attr:`.pedalLineThickness`           :func:`boundsHeight`   `uniE010`
    :attr:`.repeatBarlineDotSeparation`   :func:`stemDot`        `uniE040`
    :attr:`.repeatEndingLineThickness`    :func:`xOrigin`        `uniE030`
    :attr:`.slurEndpointThickness`        :func:`xOrigin`        `uniE1FD`
    :attr:`.slurMidpointThickness`        :func:`yMinimum`       `uniE1FD`
    :attr:`.staffLineThickness`           :func:`boundsHeight`   `uniE010`
    :attr:`.stemThickness`                :func:`xOrigin`        `uniE210`
    :attr:`.subBracketThickness`          :func:`xOrigin`        `uniE030`
    :attr:`.textEnclosureThickness`       :func:`boundsHeight`   `uniE010`
    :attr:`.thickBarlineThickness`        :func:`xOrigin`        `uniE034`
    :attr:`.thinBarlineThickness`         :func:`xOrigin`        `uniE030`
    :attr:`.thinThickBarlineSeparation`   :func:`xInner`         `uniE032`
    :attr:`.tieEndpointThickness`         :func:`xOrigin`        `uniE1FD`
    :attr:`.tieMidpointThickness`         :func:`yMinimum`       `uniE1FD`
    :attr:`.tupletBracketThickness`       :func:`xOrigin`        `uniE1FE`
    ===================================   ====================   ===========

.. note:: The setting for :attr:`.textFontFamily` must be set manually
   within the `override` parameter.

The ruler functions are available in the :mod:`~smufolib.utils.rulers` module.

This script requires SMufoLib to be installed within its executive
environment. It may also be imported as a module and contains the
following public functions:

    - :func:`calculateEngravingDefaults` - The scripts program function.
    - :func:`main` - Command line entry point.

For command-line options, run the script with :option:`--help`
argument.

"""

from __future__ import annotations
from typing import cast
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
from smufolib.utils.rulers import MAPPING, DISPATCHER
from smufolib.utils.scriptUtils import normalizeFont as _normalizeFont


Exclude = tuple[str] | list[str]
OverrideValue = int | float | tuple[str, ...] | None
Override = dict[str, OverrideValue]
MappingValue = str | int | None
Mapping = dict[str, MappingValue]
Remapping = dict[str, Mapping]
RulerType = (
    Callable[[Glyph], int | float | None] | Callable[[Glyph, int], int | float | None]
)

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
    """Calculate engraving defaults from glyph contours.

    :param font: Target font object or path to file.
    :param exclude: :class:`.EngravingDefaults` attributes to exclude.
        Defaults to :obj:`None`.
    :param override: :class:`.EngravingDefaults` attributes to manually
        override mapped to their values. Defaults to :obj:`None`.
    :param remap: :class:`.EngravingDefaults` attributes mapped to
        remappings :class:`dict`, e.g.:

        .. code-block:: python

            r = {
                'arrowShaftThickness': {
                    'ruler': 'boundsLeft',
                    'glyph': 'uniEB60',
                    'referenceIndex': 2
                }
            }

        Defaults to :obj:`None`.
    :param spaces: Whether values for overrides are given in staff
        spaces as opposed to font units. Defaults to :obj:`False`.
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

    iterator = MAPPING.items()
    if not verbose:
        iterator = tqdm(MAPPING.items())

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
        referenceIndex = mapping.get("referenceIndex")
        remapping = remap.get(key, {}) if remap else {}
        rulerName = remapping.get("ruler", rulerName)
        rulerName = cast(str, rulerName)
        ruler: RulerType = DISPATCHER[rulerName]
        glyphName = remapping.get("glyph", glyphName)
        glyphName = cast(str, glyphName)
        referenceIndex = remapping.get("referenceIndex", referenceIndex)
        referenceIndex = cast(int | None, referenceIndex)

        rulerValue = _getValue(
            font=font,
            key=key,
            glyphName=glyphName,
            ruler=ruler,
            referenceIndex=referenceIndex,
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
        error.suggestValue(item, list(MAPPING.keys()), "exclude", items=True)
    return exclude


def _normalizeOverride(override: Override | None) -> Override | None:
    # Normalize override dictionary.
    if override is None:
        return None

    error.validateType(override, dict, "override")
    for key, value in override.items():
        attributes = list(MAPPING.keys())
        error.suggestValue(key, attributes, "override", items=True)
        normalizers.normalizeEngravingDefaultsAttr(key, value)

    return override


def _normalizeRemap(remap: Remapping | None) -> Remapping | None:
    # Normalize remap dictionary.
    if remap is None:
        return None

    error.validateType(remap, dict, "remap")

    for key, value in remap.items():
        error.suggestValue(key, list(MAPPING.keys()), "remap", items=True)

        for k, v in value.items():
            error.suggestValue(
                k,
                ("ruler", "glyph", "referenceIndex"),
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
    referenceIndex: int | None,
    verbose: bool,
) -> int | float | None:
    # Get value from ruler function and print error message.
    try:
        glyph = font[glyphName]
        if referenceIndex is None:
            ruler = cast(Callable[[Glyph], int | float | None], ruler)
            return ruler(glyph)
        ruler = cast(Callable[[Glyph, int], int | float | None], ruler)
        return ruler(glyph, referenceIndex)
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
        description=stdUtils.getSummary(calculateEngravingDefaults.__doc__),
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
            """JSON string of attributes and values to manually override;
            in the format '{"<attribute name>": <value>, ...}'"""
        ),
    )

    parser.add_argument(
        "-r",
        "--remap",
        default=REMAP,
        type=json.loads,
        help=textwrap.dedent(
            """JSON string of ruler, glyph and referenceIndex remappings
            in the format: {"<attribute name>":
            '{"ruler": "<function name>", "glyph": "<glyph name>",
            "referenceIndex": <integer>}, ...}'"""
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
