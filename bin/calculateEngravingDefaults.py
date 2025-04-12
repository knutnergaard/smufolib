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

This script requires SMufoLib to be installed within its executive
environment. It may also be imported as a module and contains the
following public functions:

    - :func:`calculateEngravingDefaults` - The scripts program function.
    - :func:`main` - Command line entry point.
    - :func:`boundsLeft` - Returns absolute value of bounds x minimum.
    - :func:`boundsHeight` - Returns absolute value of bounds height.
    - :func:`stemDot` - Measures distance between stem and dot
      countour.
    - :func:`xInner` - Measures distance between two adjacent x points
      of different contours.
    - :func:`xOrigin` - Measures distance between two adjacent x points
      closest to origin.
    - :func:`yInner` - Measures distance between two adjacent y points
      of different contours.
    - :func:`yMinimum` - Measures distance between two adjacent
      low-points on y axis.

For command-line options, run the script with :option:`--help`
argument.

"""

from __future__ import annotations
from typing import TYPE_CHECKING, cast
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
    converters,
    error,
    normalizers,
    pointUtils,
    stdUtils,
)
from smufolib.utils.scriptUtils import normalizeFont as _normalizeFont


if TYPE_CHECKING:  # pragma: no cover
    from fontParts.fontshell.point import RPoint


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
MARGIN_OF_ERROR = 6
VERBOSE = False
MAPPING: Remapping = {
    "arrowShaftThickness": {
        "ruler": "xOrigin",
        "glyph": "uniEB60",
        "referenceIndex": 0,
    },
    "barlineSeparation": {"ruler": "xInner", "glyph": "uniE031", "referenceIndex": 3},
    "beamSpacing": {"ruler": "yInner", "glyph": "uniE1F9", "referenceIndex": 3},
    "beamThickness": {
        "ruler": "boundsHeight",
        "glyph": "uniE1F7",
    },
    "bracketThickness": {"ruler": "xOrigin", "glyph": "uniE003", "referenceIndex": 0},
    "dashedBarlineDashLength": {
        "ruler": "yMinimum",
        "glyph": "uniE036",
        "referenceIndex": 0,
    },
    "dashedBarlineGapLength": {
        "ruler": "yInner",
        "glyph": "uniE036",
        "referenceIndex": 3,
    },
    "dashedBarlineThickness": {
        "ruler": "xOrigin",
        "glyph": "uniE036",
        "referenceIndex": 0,
    },
    "hairpinThickness": {"ruler": "yMinimum", "glyph": "uniE53E", "referenceIndex": 0},
    "hBarThickness": {"ruler": "yMinimum", "glyph": "uniE4F0", "referenceIndex": 0},
    "legerLineExtension": {
        "ruler": "boundsLeft",
        "glyph": "uniE022",
    },
    "legerLineThickness": {
        "ruler": "boundsHeight",
        "glyph": "uniE022",
    },
    "lyricLineThickness": {
        "ruler": "boundsHeight",
        "glyph": "uniE010",
    },
    "octaveLineThickness": {
        "ruler": "boundsHeight",
        "glyph": "uniE010",
    },
    "pedalLineThickness": {
        "ruler": "boundsHeight",
        "glyph": "uniE010",
    },
    "repeatBarlineDotSeparation": {
        "ruler": "stemDot",
        "glyph": "uniE040",
        "referenceIndex": 0,
    },
    "repeatEndingLineThickness": {
        "ruler": "xOrigin",
        "glyph": "uniE030",
        "referenceIndex": 0,
    },
    "slurEndpointThickness": {
        "ruler": "xOrigin",
        "glyph": "uniE1FD",
        "referenceIndex": 0,
    },
    "slurMidpointThickness": {
        "ruler": "yMinimum",
        "glyph": "uniE1FD",
        "referenceIndex": 0,
    },
    "staffLineThickness": {
        "ruler": "boundsHeight",
        "glyph": "uniE010",
    },
    "stemThickness": {"ruler": "xOrigin", "glyph": "uniE210", "referenceIndex": 0},
    "subBracketThickness": {
        "ruler": "xOrigin",
        "glyph": "uniE030",
        "referenceIndex": 0,
    },
    "textEnclosureThickness": {
        "ruler": "boundsHeight",
        "glyph": "uniE010",
    },
    "textFontFamily": {},
    "thickBarlineThickness": {
        "ruler": "xOrigin",
        "glyph": "uniE034",
        "referenceIndex": 0,
    },
    "thinBarlineThickness": {
        "ruler": "xOrigin",
        "glyph": "uniE030",
        "referenceIndex": 0,
    },
    "thinThickBarlineSeparation": {
        "ruler": "xInner",
        "glyph": "uniE032",
        "referenceIndex": 3,
    },
    "tieEndpointThickness": {
        "ruler": "xOrigin",
        "glyph": "uniE1FD",
        "referenceIndex": 0,
    },
    "tieMidpointThickness": {
        "ruler": "yMinimum",
        "glyph": "uniE1FD",
        "referenceIndex": 0,
    },
    "tupletBracketThickness": {
        "ruler": "xOrigin",
        "glyph": "uniE1FE",
        "referenceIndex": 0,
    },
}


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

    dispatcher: dict[str, RulerType] = {
        "boundsHeight": boundsHeight,
        "boundsLeft": boundsLeft,
        "stemDot": stemDot,
        "xInner": xInner,
        "xOrigin": xOrigin,
        "yInner": yInner,
        "yMinimum": yMinimum,
    }

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
        ruler: RulerType = dispatcher[rulerName]
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


# ------
# Rulers
# ------


def boundsHeight(glyph: Glyph) -> int | float | None:
    """Height of the glyph bounds.

    :param glyph: Source :class:`.Glyph` of contours to measure.

    """
    return converters.toIntIfWhole(glyph.bounds[3] - glyph.bounds[1])


def boundsLeft(glyph: Glyph) -> int | float | None:
    """Return absolute value of the glyph bounds x minimum value.

    :param glyph: Source :class:`.Glyph` of contours to measure.

    """
    return converters.toIntIfWhole(abs(glyph.bounds[0]))


def stemDot(glyph: Glyph, referenceIndex: int = 0) -> int | float | None:
    """Calculate distance between stem and dot countour.

    :param glyph: Source :class:`.Glyph` of contours to measure.
    :param referenceIndex: referenceIndex of reference point. Defaults to ``0``.

    """
    curves = sorted(pointUtils.getPoints(glyph, "curve"), key=lambda p: p.position.x)
    lines = sorted(
        pointUtils.getPoints(glyph, "line"), reverse=True, key=lambda p: p.position.x
    )
    if not lines or not curves:
        return None

    reference = curves[referenceIndex]

    for point in lines:
        if point.contourIndex == reference.contourIndex:
            continue
        return converters.toIntIfWhole(abs(point.position.x - reference.position.x))

    return None


def xInner(glyph: Glyph, referenceIndex: int = 0) -> int | float | None:
    """Calculate distance between adjacent x points of two contours.

    :param glyph: Source :class:`.Glyph` of contours to measure.
    :param referenceIndex: referenceIndex of reference point. Defaults to ``0``.

    """
    points = sorted(pointUtils.getPoints(glyph), key=lambda p: p.position.x)
    reference = points[referenceIndex]

    for point in points:
        if point.contourIndex == reference.contourIndex or not _areAdjacent(
            point, reference, axis="y"
        ):
            continue

        return converters.toIntIfWhole(abs(point.position.x - reference.position.x))

    return None


def xOrigin(glyph: Glyph, referenceIndex: int = 0) -> int | float | None:
    """Calculate distance between adjacent x points closest to origin.

    :param glyph: Source :class:`.Glyph` of contours to measure.
    :param referenceIndex: referenceIndex of reference point. Defaults to ``0``.

    """
    points = sorted(pointUtils.getPoints(glyph), key=lambda p: sum(p.position))
    reference = points[referenceIndex]

    for point in points:
        if (
            point.position.x == reference.position.x
            or point.contourIndex != reference.contourIndex
            or not _areAdjacent(point, reference, axis="y")
        ):
            continue
        return converters.toIntIfWhole(abs(point.position.x - reference.position.x))

    return None


def yInner(glyph: Glyph, referenceIndex: int = 0) -> int | float | None:
    """Calculate distance between adjacent y points of two contours.

    :param glyph: Source :class:`.Glyph` of contours to measure.
    :param referenceIndex: referenceIndex of reference point. Defaults to ``0``.

    """
    points = sorted(pointUtils.getPoints(glyph), key=lambda p: p.position.y)
    reference = points[referenceIndex]
    for point in points:
        if point.contourIndex == reference.contourIndex or not _areAdjacent(
            point, reference, axis="x"
        ):
            continue
        return converters.toIntIfWhole(abs(point.position.y - reference.position.y))

    return None


def yMinimum(glyph: Glyph, referenceIndex: int = 0) -> int | float | None:
    """Calculate distance between adjacent low-points on axis y.

    :param glyph: Source :class:`.Glyph` of contours to measure.
    :param referenceIndex: referenceIndex of reference point. Defaults
        to ``0``.

    """
    points = sorted(pointUtils.getPoints(glyph), key=lambda p: p.position.y)
    reference = points[referenceIndex]

    for point in points:
        if (
            point.position.y == reference.position.y
            or point.contourIndex != reference.contourIndex
            or not _areAdjacent(point, reference, axis="x")
        ):
            continue
        return converters.toIntIfWhole(abs(point.position.y - reference.position.y))

    return None


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


def _areAdjacent(point1: RPoint, point2: RPoint, axis: str | None) -> bool:
    # Check if points are adjacent on axis.
    # Employ margin of error for point placement.

    def withinRange(num1: int, num2: int) -> bool:
        return num2 - MARGIN_OF_ERROR <= num1 <= num2 + MARGIN_OF_ERROR

    x1, x2 = point1.position.x, point2.position.x
    y1, y2 = point1.position.y, point2.position.y

    if axis == "x":
        checkAxis = withinRange(x1, x2)
    else:
        checkAxis = withinRange(y1, y2)

    return point1 != point2 and checkAxis


if __name__ == "__main__":
    main()
