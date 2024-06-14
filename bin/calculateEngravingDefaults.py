#!/usr/bin python3
# coding: utf-8

"""This script measures and sets engraving defaults based on the
dimensions, registration, metrics and/or point placement of appropriate
font glyphs.

With limited means of identification and control over the necessary
parameters, the script presently relies on a rather rudimentary and
somewhat error-prone process for calculating values. For this reason,
the results should be used only as a starting point for setting the
values of
:class:`~smufolib.objects.engravingDefaults.EngravingDefaults`
attributes.

The user has the option to override or skip any automatic measurements,
as well as reassign attributes to different ruler functions or glyphs
than the default. This is particularly useful for automatic
measurements of line widths for e.g. octave lines, pedal lines or
repeat endings, which are not represented by a particular SMuFL glyph,
but are often based on the thickness of other lines, such as staff
lines, leger lines, barlines, etc., depending on the desired
thickness.

.. note:: The setting
   for
   :attr:`~smufolib.objects.engravingDefaults.EngravingDefaults.textFontFamily`,
   which involves no measuring or calculation, has to be set manually
   with the ``override`` parameter.

This script requires that SMufoLib be installed within its executive
environment. It may also be imported as a module and contains the
following public functions:

    * :func:`calculateEngravingDefaults` - The scripts program function.
    * :func:`main` – Command line entry point.
    * :func:`boundsLeft` – Returns absolute value of bounds x minimum.
    * :func:`boundsHeight` – Returns absolute value of bounds height.
    * :func:`stemDot` – Measures distance between stem and dot
       countour.
    * :func:`xInner` – Measures distance between two adjacent x points
       of different contours.
    * :func:`xOrigin` – Measures distance between two adjacent x points
      closest to origin.
    * :func:`yInner` – Measures distance between two adjacent y points
       of different contours.
    * :func:`yMinimum` – Measures distance between two adjacent
       low-points on y axis.

"""
from __future__ import annotations
from typing import TYPE_CHECKING
import argparse
import json
import textwrap
from pathlib import Path

from smufolib import Font, cli, config, pointUtils

if TYPE_CHECKING:
    from fontParts.fontshell.point import RPoint
    from smufolib.objects.glyph import Glyph

CONFIG = config.load()

# Parameter defaults
EXCLUDE = None
OVERRIDE = None
SPACES = False
REMAP = None
MARGIN_OF_ERROR = 6

# pylint: disable=invalid-name, too-many-arguments


def calculateEngravingDefaults(font: Font | Path | str,
                               exclude: str | list | None = EXCLUDE,
                               override: dict[str, int |
                                              float] | None = OVERRIDE,
                               remap: dict[str, dict[str, str | int]
                                           ] | None = REMAP,
                               spaces: bool = SPACES) -> None:
    """Calculate engraving defaults from glyph contours.

    :param font: Target font object or path to file.
    :param exclude: :class:`~smufolib.objects.engravingDefaults.EngravingDefaults`
     attributes to exclude. Defaults to ``None``.
    :param override: :class:`~smufolib.objects.engravingDefaults.EngravingDefaults`
     attributes to manually override mapped to their values. Defaults to ``None``.
    :param remap: :class:`~smufolib.objects.engravingDefaults.EngravingDefaults`
     attributes mapped to remappings :class:`dict`, e.g.:

        .. code-block:: python

            r = {
                'arrowShaftThickness': {
                    'ruler': 'boundsLeft',
                    'glyph': 'uniEB60',
                    'referenceIndex': 2
                }
            }

     Defaults to ``None``.
    :param spaces: set units of measurement to font units
     or :attr:`~smufolib.objects.smufl.Smufl.spaces`. Defaults to
     ``False``.

    """
    dispatcher = {
        'boundsHeight': boundsHeight,
        'boundsLeft': boundsLeft,
        'stemDot': stemDot,
        'xInner': xInner,
        'xOrigin': xOrigin,
        'yInner': yInner,
        'yMinimum': yMinimum,
    }

    defaults = {
        'arrowShaftThickness': (xOrigin, 'uniEB60'),
        'barlineSeparation': (xInner, 'uniE031'),
        'beamSpacing': (yInner, 'uniE1F9'),
        'beamThickness': (boundsHeight, 'uniE1F7'),
        'bracketThickness': (xOrigin, 'uniE003'),
        'dashedBarlineDashLength': (yMinimum, 'uniE036'),
        'dashedBarlineGapLength': (yInner, 'uniE036'),
        'dashedBarlineThickness': (xOrigin, 'uniE036'),
        'hairpinThickness': (yMinimum, 'uniE53E'),
        'hBarThickness': (yMinimum, 'uniE4F0'),
        'legerLineExtension': (boundsLeft, 'uniE022'),
        'legerLineThickness': (boundsHeight, 'uniE022'),
        'lyricLineThickness': (boundsHeight, 'uniE010'),
        'octaveLineThickness': (boundsHeight, 'uniE010'),
        'pedalLineThickness': (boundsHeight, 'uniE010'),
        'repeatBarlineDotSeparation': (stemDot, 'uniE040'),
        'repeatEndingLineThickness': (xOrigin, 'uniE030'),
        'slurEndpointThickness': (xOrigin, 'uniE1FD'),
        'slurMidpointThickness': (yMinimum, 'uniE1FD'),
        'staffLineThickness': (boundsHeight, 'uniE010'),
        'stemThickness': (xOrigin, 'uniE210'),
        'subBracketThickness': (xOrigin, 'uniE030'),
        'textEnclosureThickness': (boundsHeight, 'uniE010'),
        'thickBarlineThickness': (xOrigin, 'uniE034'),
        'thinBarlineThickness': (xOrigin, 'uniE030'),
        'thinThickBarlineSeparation': (xInner, 'uniE032'),
        'tieEndpointThickness': (xOrigin, 'uniE1FD'),
        'tieMidpointThickness': (yMinimum, 'uniE1FD'),
        'tupletBracketThickness': (xOrigin, 'uniE1FE')
    }

    font.smufl.spaces = False

    for key, mapping in defaults.items():
        if exclude and key in exclude:
            continue

        ruler, glyph = mapping
        referenceIndex = None
        if remap and key in remap:
            if 'ruler' in remap[key]:
                ruler = dispatcher[remap[key]['ruler']]
            if 'glyph' in remap[key]:
                glyph = remap[key]['glyph']
            referenceIndex = remap[key].get('referenceIndex')

        value = ruler(font[glyph])
        if referenceIndex:
            value = ruler(font[glyph], referenceIndex=referenceIndex)
        if override:
            value = override.get(key)
            if spaces:
                value = font.smufl.toUnits(override.get(key))
            elif 'textFontFamily' in override:
                value = override['textFontFamily']

        setattr(font.smufl.engravingDefaults, key, value)

        if spaces:
            value = font.smufl.toSpaces(value)
        print(f"Setting attribute '{key}': {value}")

    font.save()
    print("Done!")


def main():
    """Command line entry point."""
    args = _parseArgs()
    calculateEngravingDefaults(
        args.font, args.exclude, args.remap, args.override, args.spaces)


# ------
# Rulers
# ------


def boundsHeight(glyph: Glyph) -> int:
    """Height of the glyph bounds.

    :param glyph: Source :class:`~smufolib.objects.glyph.Glyph` of
     contours to measure.

    """
    return glyph.bounds[3] - glyph.bounds[1]


def boundsLeft(glyph: Glyph) -> int:
    """Absolute value of bounds x minimum.

    :param glyph: Source :class:`~smufolib.objects.glyph.Glyph` of
     contours to measure.

    """
    return abs(glyph.bounds[0])


def stemDot(glyph: Glyph, referenceIndex: int=0) -> int:
    """Distance between stem and dot countour.

    :param glyph: Source :class:`~smufolib.objects.glyph.Glyph` of
     contours to measure.
    :param referenceIndex: index of reference point.

    """
    curves = sorted(pointUtils.getPoints(glyph, 'curve'),
                    key=lambda p: p.position.x)
    lines = sorted(pointUtils.getPoints(glyph, 'line'),
                   reverse=True, key=lambda p: p.position.x)

    reference = curves[referenceIndex]
    for point in lines:
        if not point.contourIndex != reference.contourIndex:
            continue
        return abs(point.position.x - reference.position.x)


def xInner(glyph: Glyph, referenceIndex: int=3) -> int:
    """Distance between two adjacent x points of different contours.

    :param glyph: Source :class:`~smufolib.objects.glyph.Glyph` of
     contours to measure.
    :param referenceIndex: index of reference point.

    """
    points = sorted(pointUtils.getPoints(glyph), key=lambda p: p.position.x)
    reference = points[referenceIndex]

    for point in points:
        if not (point.contourIndex != reference.contourIndex
                and _areAdjacent(point, reference, axis='y')):
            continue
        return abs(point.position.x - reference.position.x)


def xOrigin(glyph: Glyph, referenceIndex: int=0) -> int:
    """Distance between two adjacent x points closest to origin.

    :param glyph: Source :class:`~smufolib.objects.glyph.Glyph` of
     contours to measure.
    :param referenceIndex: index of reference point.

    """
    points = sorted(pointUtils.getPoints(glyph), key=lambda p: sum(p.position))
    reference = points[referenceIndex]

    for point in points:
        if not (point.position.x != reference.position.x
                and point.contourIndex == reference.contourIndex
                and _areAdjacent(point, reference, axis='y')):
            continue
        return abs(point.position.x - reference.position.x)


def yOrigin(glyph: Glyph, referenceIndex: int=0) -> int:
    """Distance between two adjacent x points closest to origin.

    :param glyph: Source :class:`~smufolib.objects.glyph.Glyph` of
     contours to measure.
    :param referenceIndex: index of reference point.

    """
    points = sorted(pointUtils.getPoints(glyph), key=lambda p: sum(p.position))
    reference = points[referenceIndex]

    for point in points:
        if not (point.position.x != reference.position.x
                and point.contourIndex == reference.contourIndex
                and _areAdjacent(point, reference, axis='y')):
            continue
        return abs(point.position.x - reference.position.x)


def yInner(glyph: Glyph, referenceIndex: int=3) -> int:
    """Distance between two adjacent y points of different contours.

    :param glyph: Source :class:`~smufolib.objects.glyph.Glyph` of
     contours to measure.
    :param referenceIndex: index of reference point.

    """
    points = sorted(pointUtils.getPoints(glyph), key=lambda p: p.position.y)
    reference = points[referenceIndex]
    for point in points:
        if not (point.contourIndex != reference.contourIndex
                and _areAdjacent(point, reference, axis='x')):
            continue
        return abs(point.position.y - reference.position.y)


def yMinimum(glyph: Glyph, referenceIndex: int=0) -> int:
    """Distance between two adjacent low-points on axis y.

    :param glyph: Source :class:`~smufolib.objects.glyph.Glyph` of
     contours to measure.
    :param referenceIndex: index of reference point.

    """
    points = sorted(pointUtils.getPoints(glyph), key=lambda p: p.position.y)
    reference = points[referenceIndex]

    for point in points:
        if not (point.position.y != reference.position.y
                and point.contourIndex == reference.contourIndex
                and _areAdjacent(point, reference, axis='x')):
            continue
        return abs(point.position.y - reference.position.y)


def _areAdjacent(point1: RPoint, point2: RPoint,
                 axis: str | None) -> bool:
    # Check if points are adjacent on axis.
    # Employ margin of error for point placement.

    def withinRange(num1: int, num2: int) -> bool:
        return num2 - MARGIN_OF_ERROR <= num1 <= num2 + MARGIN_OF_ERROR

    x1, x2 = point1.position.x, point2.position.x
    y1, y2 = point1.position.y, point2.position.y

    if axis == 'x':
        checkAxis = withinRange(x1, x2)
    elif axis == 'y':
        checkAxis = withinRange(y1, y2)
    else:
        checkAxis = withinRange(x1, x2) or withinRange(y1, y2)
    return point1 != point2 and checkAxis


def _parseArgs() -> argparse.Namespace:
    # Parse command line arguments and options.
    parser = argparse.ArgumentParser(
        parents=[cli.commonParser('font', exclude=EXCLUDE, spaces=SPACES)],
        formatter_class=argparse.RawTextHelpFormatter,
        description=__doc__)

    parser.add_argument(
        '-o', '--override',
        default=OVERRIDE,
        type=json.loads,
        help=textwrap.dedent("""\
            JSON string of attributes and values to manually override, e.g.
            {
                "arrowShaftThickness": <number>,
                "barlineSeparation": <number>
            }
            """)
    )

    parser.add_argument(
        '-r', '--remap',
        default=REMAP,
        type=json.loads,
        help=textwrap.dedent("""\
            JSON string of ruler, glyph and referenceIndex remappings, e.g.
            {
                "arrowShaftThickness": {
                    "ruler": "<function name>",
                    "glyph": "<glyph name>",
                    "referenceIndex": <number>
                }
            }
            """)
    )

    return parser.parse_args()


if __name__ == '__main__':
    main()
