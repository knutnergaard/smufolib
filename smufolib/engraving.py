"""Engraving module for SMufoLib.

This module contains functionality to extract engraving default values
from appropriate font glyphs. With limited means of contour and point
identification and control, this is presently a rather rudimentary
process, with more than negligible chances for errors.

For this reason, please use the module with care. and override any
erronous values by assigning them explicitly in smufolib.cfg.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Iterable, NamedTuple, Tuple
from collections import namedtuple

from fontParts.fontshell import RGlyph, RComponent, RPoint

if TYPE_CHECKING:
    from smufolib.font import Font

# pylint: disable=too-many-ancestors, invalid-name


def getEngravingDefaults(font: Font,
                         **kwargs: str
                         ) -> Dict[str, float | Tuple[str]]:
    """Extract engraving default values from font glyphs.

    :param font: SMufoLib Font object.
    """
    functions = {
        'arrowShaftThickness': _originX(font['uniEB60']),
        'barlineSeparation': _innerX(font['uniE031']),
        'beamSpacing': _innerY(font['uniE1F9']),
        'beamThickness': _minY(font['uniE1F7']),
        'bracketThickness': _originX(font['uniE003']),
        'dashedBarlineDashLength': _minY(font['uniE036']),
        'dashedBarlineGapLength': _innerY(font['uniE036']),
        'dashedBarlineThickness': _originX(font['uniE036']),
        'hairpinThickness': _minY(font['uniE53E']),
        'legerLineExtension': _boundsLeft(font['uniE022']),
        'legerLineThickness': _boundsHeight(font['uniE022']),
        'lyricLineThickness': _boundsHeight(font['uniE022']),
        'octaveLineThickness': _boundsHeight(font['uniE022']),
        'pedalLineThickness': _boundsHeight(font['uniE022']),
        'repeatBarlineDotSeparation': _stemDot(font['uniE040']),
        'repeatEndingLineThickness': _boundsHeight(font['uniE022']),
        'slurEndpointThickness': _originX(font['uniE1FD']),
        'slurMidpointThickness': _minY(font['uniE1FD']),
        'staffLineThickness': _minY(font['uniE010']),
        'stemThickness': _originX(font['uniE210']),
        'subBracketThickness': _boundsHeight(font['uniE022']),
        'textFontFamily': [],
        'textEnclosureThickness': _boundsHeight(font['uniE022']),
        'thickBarlineThickness': _originX(font['uniE034']),
        'thinBarlineThickness': _originX(font['uniE030']),
        'tieEndpointThickness': _originX(font['uniE1FD']),
        'tieMidpointThickness': _minY(font['uniE1FD']),
        'tupletBracketThickness': _originX(font['uniE1FE'])
    }

    return {k: v if k not in kwargs or kwargs[k] is None
            else kwargs[k] for k, v in functions.items()}


def _areAdjacent(point1: RPoint,
                 point2: RPoint,
                 axis: str | None = None
                 ) -> bool:
    # Checks if points are ajacent accross axis.
    # Employs a margin of error to account for inaccurate placement.
    margin = 6

    def withinRange(num1: int, num2: int) -> bool:
        return num2 - margin <= num1 <= num2 + margin

    x1, x2 = point1.position.x, point2.position.x
    y1, y2 = point1.position.y, point2.position.y

    if axis == 'x':
        checkAxis = withinRange(x1, x2)
    elif axis == 'y':
        checkAxis = withinRange(y1, y2)
    else:
        checkAxis = withinRange(x1, x2) or withinRange(y1, y2)

    return point1 != point2 and checkAxis


def _decomposePoints(component: RComponent,
                     types: str | Tuple[str]) -> Tuple[str, Tuple[int], int]:
    # Gets points and offset position from glyph component.
    Point, Position = _namedTuples()

    offset = tuple(int(round(o)) for o in component.offset)
    glyph = component.font[component.baseGlyph]

    def addTuples(*tuples):
        return tuple(map(sum, zip(*tuples)))

    points = []
    for point in _flatten(glyph.contours):
        if point.type in types:
            points.append(Point(point.type,
                                Position(*addTuples(point.position, offset)),
                                component.index))
    return points


def _getPoints(glyph: RGlyph,
               types: str | Tuple[str] = ('line', 'curve', 'qcurve')
               ) -> Tuple[NamedTuple]:
    # Returns tuple of points.
    Point, Position = _namedTuples()

    points = tuple(Point(p.type, Position(*p.position), p.contour.index)
                   for p in _flatten(glyph.rGlyph.contours) if p.type in types)

    if glyph.rGlyph.components:
        points += tuple(Point(p[0], Position(*p[1]), p[2])
                        for c in glyph.rGlyph.components
                        for p in _decomposePoints(c, types))
    return points


def _innerX(glyph: RGlyph, referenceIndex: int = 3) -> int:
    # Finds distance between two adjacent x-points of different contours.
    points = sorted(_getPoints(glyph), key=lambda p: p.position.x)
    reference = points[referenceIndex]

    for point in points:
        if not (point.contourIndex != reference.contourIndex
                and _areAdjacent(point, reference, axis='y')):
            continue
        return abs(point.position.x - reference.position.x)


def _innerY(glyph: RGlyph, referenceIndex: int = 3) -> int:
    # Finds distance between two adjacent y-points of different contours.
    points = sorted(_getPoints(glyph), key=lambda p: p.position.y)
    reference = points[referenceIndex]
    for point in points:
        if not (point.contourIndex != reference.contourIndex
                and _areAdjacent(point, reference, axis='x')):
            continue
        return abs(point.position.y - reference.position.y)


def _minY(glyph: RGlyph) -> int:
    # Finds distance between two adjacent low-points on axis y.
    points = sorted(_getPoints(glyph), key=lambda p: p.position.y)
    reference = points[0]

    for point in points:
        if not (point.position.y != reference.position.y
                and point.contourIndex == reference.contourIndex
                and _areAdjacent(point, reference, axis='x')):
            continue
        return abs(point.position.y - reference.position.y)


def _originX(glyph: RGlyph) -> int:
    # Finds distance between two adjacent x-points closest to origin.
    points = sorted(_getPoints(glyph), key=lambda p: sum(p.position))
    reference = points[0]

    for point in points:
        if not (point.position.x != reference.position.x
                and point.contourIndex == reference.contourIndex
                and _areAdjacent(point, reference, axis='y')):
            continue
        return abs(point.position.x - reference.position.x)


def _stemDot(glyph: RGlyph) -> int:
    # Finds distance between stem and dot countour.
    curves = sorted(_getPoints(glyph, 'curve'), key=lambda p: p.position.x)
    lines = sorted(_getPoints(glyph, 'line'),
                   reverse=True, key=lambda p: p.position.x)

    reference = curves[0]
    for point in lines:
        if not point.contourIndex != reference.contourIndex:
            continue
        return abs(point.position.x - reference.position.x)


def _boundsLeft(glyph: RGlyph) -> int:
    # Returns absolute value of bounds min x.
    return abs(glyph.rGlyph.bounds[0])


def _boundsHeight(glyph: RGlyph) -> int:
    # Returns absolute bounds height.
    return sum((abs(glyph.rGlyph.bounds[1]), abs(glyph.rGlyph.bounds[3])))


def _flatten(iterable: Iterable[Any], depth: int = None) -> Iterable[Any]:
    """Flatten irregularly nested iterables of any depth."""
    for item in iterable:
        if (not isinstance(item, Iterable)
                or isinstance(item, (str, bytes)) or depth == 0):
            yield item
        elif depth is None:
            yield from _flatten(item)
        else:
            yield from _flatten(item, depth - 1)


def _namedTuples() -> NamedTuple:
    # Returns named tuples for point and position values.
    Point = namedtuple('Point', ['types', 'position', 'contourIndex'])
    Position = namedtuple('Position', ['x', 'y'])
    return Point, Position
