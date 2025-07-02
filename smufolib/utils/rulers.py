"""Measurement utilities for calculating glyph geometry.

This module provides functions to retrieve, measure and inspect various parts of glyphs.
It also defines:

- :data:`ENGRAVING_DEFAULTS_MAPPING`, the default association between ruler functions
  and glyphs used for calculating :class:`.EngravingDefaults` attribute values.
- :data:`DISPATCHER`, for dynamically executing measurement operations by function name.

To import the module:

    >>> from smufolib import rulers

"""

from __future__ import annotations
from typing import TYPE_CHECKING, Generator
from collections.abc import Callable
from math import dist

from smufolib.utils import converters

if TYPE_CHECKING:  # pragma: no cover
    from fontParts.fontshell.point import RPoint
    from fontParts.fontshell.segment import RSegment
    from fontParts.fontshell.contour import RContour
    from smufolib.objects.glyph import Glyph

Bounds = tuple[int | float, int | float, int | float, int | float]
Remapping = dict[str, dict[str, str]]
RulerType = Callable[["Glyph"], int | float | None]

TOLERANCE: int | float = 6
TYPES: str | tuple[str, ...] = ("line", "curve", "qcurve")

#: Default mapping of rulers and glyphs to :class:`EngravingDefaults` attributes.
ENGRAVING_DEFAULTS_MAPPING: Remapping = {
    "arrowShaftThickness": {
        "ruler": "xStrokeWidthAtOrigin",
        "glyph": "uniEB60",
    },
    "barlineSeparation": {
        "ruler": "xDistanceBetweenContours",
        "glyph": "uniE031",
    },
    "beamSpacing": {
        "ruler": "yDistanceBetweenContours",
        "glyph": "uniE1F9",
    },
    "beamThickness": {
        "ruler": "glyphBoundsHeight",
        "glyph": "uniE1F7",
    },
    "bracketThickness": {
        "ruler": "xStrokeWidthAtOrigin",
        "glyph": "uniE003",
    },
    "dashedBarlineDashLength": {
        "ruler": "yStrokeWidthAtMinimum",
        "glyph": "uniE036",
    },
    "dashedBarlineGapLength": {
        "ruler": "yDistanceBetweenContours",
        "glyph": "uniE036",
    },
    "dashedBarlineThickness": {
        "ruler": "glyphBoundsWidth",
        "glyph": "uniE036",
    },
    "hairpinThickness": {
        "ruler": "wedgeArmStrokeWidth",
        "glyph": "uniE53E",
    },
    "hBarThickness": {
        "ruler": "yStrokeWidthAtMinimum",
        "glyph": "uniE4F0",
    },
    "legerLineExtension": {
        "ruler": "glyphBoundsXMinAbs",
        "glyph": "uniE022",
    },
    "legerLineThickness": {
        "ruler": "glyphBoundsHeight",
        "glyph": "uniE022",
    },
    "lyricLineThickness": {
        "ruler": "glyphBoundsHeight",
        "glyph": "uniE010",
    },
    "octaveLineThickness": {
        "ruler": "glyphBoundsHeight",
        "glyph": "uniE010",
    },
    "pedalLineThickness": {
        "ruler": "glyphBoundsHeight",
        "glyph": "uniE010",
    },
    "repeatBarlineDotSeparation": {
        "ruler": "xDistanceStemToDot",
        "glyph": "uniE040",
    },
    "repeatEndingLineThickness": {
        "ruler": "xStrokeWidthAtOrigin",
        "glyph": "uniE030",
    },
    "slurEndpointThickness": {
        "ruler": "xStrokeWidthAtOrigin",
        "glyph": "uniE1FD",
    },
    "slurMidpointThickness": {
        "ruler": "yStrokeWidthAtMinimum",
        "glyph": "uniE1FD",
    },
    "staffLineThickness": {
        "ruler": "glyphBoundsHeight",
        "glyph": "uniE010",
    },
    "stemThickness": {
        "ruler": "glyphBoundsWidth",
        "glyph": "uniE210",
    },
    "subBracketThickness": {
        "ruler": "xStrokeWidthAtOrigin",
        "glyph": "uniE030",
    },
    "textEnclosureThickness": {
        "ruler": "glyphBoundsHeight",
        "glyph": "uniE010",
    },
    "textFontFamily": {},
    "thickBarlineThickness": {
        "ruler": "glyphBoundsWidth",
        "glyph": "uniE034",
    },
    "thinBarlineThickness": {
        "ruler": "glyphBoundsWidth",
        "glyph": "uniE030",
    },
    "thinThickBarlineSeparation": {
        "ruler": "xDistanceBetweenContours",
        "glyph": "uniE032",
    },
    "tieEndpointThickness": {
        "ruler": "xStrokeWidthAtOrigin",
        "glyph": "uniE1FD",
    },
    "tieMidpointThickness": {
        "ruler": "yStrokeWidthAtMinimum",
        "glyph": "uniE1FD",
    },
    "tupletBracketThickness": {
        "ruler": "xStrokeWidthAtOrigin",
        "glyph": "uniE1FE",
    },
}

# ------
# Rulers
# ------


def glyphBoundsHeight(glyph: Glyph) -> int | float | None:
    """Return height of the glyph's bounding box.

    :param glyph: Source :class:`.Glyph` of contours to measure.

    Example:

        >>> glyph = font["uniE050"]
        >>> rulers.glyphBoundsHeight(glyph)
        1801

    """
    boundsList = [c.bounds for c in getGlyphContours(glyph)]
    bounds = combineBounds(boundsList)
    if not bounds:
        return None
    return converters.toIntIfWhole(bounds[3] - bounds[1])


def glyphBoundsWidth(glyph: Glyph) -> int | float | None:
    """Return width of the glyph's bounding box.

    :param glyph: Source :class:`.Glyph` of contours to measure.

    Example:

        >>> glyph = font["uniE050"]
        >>> rulers.glyphBoundsWidth(glyph)
        648

    """
    boundsList = [c.bounds for c in getGlyphContours(glyph)]
    bounds = combineBounds(boundsList)
    if not bounds:
        return None
    return converters.toIntIfWhole(bounds[2] - bounds[0])


def glyphBoundsXMinAbs(glyph: Glyph) -> int | float | None:
    """Return absolute value of glyph's *xMin* bound.

    :param glyph: Source :class:`.Glyph` of contours to measure.

    Example::

        >>> glyph = font["uniE022"]
        >>> rulers.glyphBoundsXMinAbs(glyph)
        80

    """
    boundsList = [c.bounds for c in getGlyphContours(glyph)]
    bounds = combineBounds(boundsList)
    if not bounds:
        return None
    return converters.toIntIfWhole(abs(bounds[0]))


def xDistanceStemToDot(glyph: Glyph) -> int | float | None:
    """Measure horizontal distance between a stem and a dot contour.

    The contours may be placed on either side of each other.

    :param glyph: Source :class:`.Glyph` of contours to measure.

    Example::

        >>> glyph = font["uniE040"]
        >>> rulers.glyphBoundsXMinAbs(glyph)
        63

    """
    dotPoints = [
        p for p in getGlyphPoints(glyph) if all(s.type != "line" for s in p.contour)
    ]
    stemPoints = list(getGlyphPoints(glyph, "line"))

    if not stemPoints or not dotPoints:
        return None

    # reference point should be the point in the dot contour facing the stem.
    referencePoint = min(dotPoints, key=lambda p: p.x)
    closestStemPoint = max(stemPoints, key=lambda p: p.x)
    if referencePoint.x < closestStemPoint.x:
        referencePoint = max(dotPoints, key=lambda p: p.x)
        closestStemPoint = min(stemPoints, key=lambda p: p.x)

    return converters.toIntIfWhole(abs(closestStemPoint.x - referencePoint.x))


def xDistanceBetweenContours(glyph: Glyph) -> int | float | None:
    """Measure horizontal distance between two adjacent contours in a glyph.

    :param glyph: Source :class:`.Glyph` of contours to measure.

    Example::

        >>> glyph = font["uniE031"]
        >>> rulers.xDistanceBetweenContours(glyph)
        85

    """
    points = sorted(getGlyphPoints(glyph), key=lambda p: p.x)
    if not points:
        return None

    # Reference point should be the right point of the left contour.
    referencePoint = max(points[0].contour.points, key=lambda p: p.x)

    for point in points:
        if point.contour.index == referencePoint.contour.index:
            continue

        return converters.toIntIfWhole(abs(point.x - referencePoint.x))

    return None


def yDistanceBetweenContours(glyph: Glyph) -> int | float | None:
    """Measure vertical distance between two adjacent contours in a glyph.

    :param glyph: Source :class:`.Glyph` of contours to measure.

    Example::

        >>> glyph = font["uniE036"]
        >>> rulers.yDistanceBetweenContours(glyph)
        119

    """
    points = sorted(getGlyphPoints(glyph), key=lambda p: p.y)
    if not points:
        return None

    # Reference point should be the top point of the bottom contour.
    referencePoint = max(points[0].contour.points, key=lambda p: p.y)

    for point in points:
        if point.contour.index == referencePoint.contour.index:
            continue

        return converters.toIntIfWhole(abs(point.y - referencePoint.y))

    return None


def xStrokeWidthAtOrigin(glyph: Glyph) -> int | float | None:
    """Measure horizontal distance between aligned points closest to origin.

    :param glyph: Source :class:`.Glyph` of contours to measure.

    Example::

        >>> glyph = font["uniE1FE"]
        >>> rulers.xStrokeWidthAtOrigin(glyph)
        32

    """
    points = sorted(getGlyphPoints(glyph), key=lambda p: abs(p.x) + abs(p.y))
    if not points:
        return None

    referencePoint, *rest = points

    for point in rest:
        if point.contour.index != referencePoint.contour.index:
            continue
        if point.x == referencePoint.x:
            continue
        if not areAlligned((referencePoint, point), axis="y"):
            continue
        return converters.toIntIfWhole(abs(point.x - referencePoint.x))

    return None


def yStrokeWidthAtMinimum(glyph: Glyph) -> int | float | None:
    """Measure vertical distance between aligned low-points in the glyph.

    :param glyph: Source :class:`.Glyph` of contours to measure.

    Example::

        >>> glyph = font["uniE1FD"]
        >>> rulers.yStrokeWidthAtMinimum(glyph)
        50

    """

    points = sorted(getGlyphPoints(glyph), key=lambda p: p.y)
    if not points:
        return None

    referencePoint, *rest = points

    for point in rest:
        if point.contour.index != referencePoint.contour.index:
            continue
        if point.y == referencePoint.y:
            continue
        if not areAlligned((referencePoint, point), axis="x"):
            continue
        return converters.toIntIfWhole(abs(point.y - referencePoint.y))

    return None


def wedgeArmStrokeWidth(glyph: Glyph):
    """Measure thickness of arm in a wedge-shaped glyph.

    :param glyph: Source :class:`.Glyph` of contours to measure.

    Example::

        >>> glyph = font["uniE1FD"]
        >>> rulers.yStrokeWidthAtMinimum(glyph)
        50

    """

    def euclidean(p1, p2):
        return dist((p1.x, p1.y), (p2.x, p2.y))

    points = sorted(getGlyphPoints(glyph, "line"), key=lambda p: p.y)

    referencePoint = max(points, key=lambda p: p.x)

    candidates = [p for p in points if p is not referencePoint]
    nearest = min(candidates, key=lambda p: euclidean(p, referencePoint))

    return round(euclidean(referencePoint, nearest))


def areAlligned(
    points: tuple[RPoint, ...], axis: str, tolerance: int | float = TOLERANCE
) -> bool:
    """Check if the specified `points` are aligned on `axis`.

    :param points: The points to check for alignment.
    :param axis: The axis (``"x"`` or ``"y"``) accross which to check for alignment.
    :param tolerance: The tolerance for misalignment to apply in font units.
        Defaults to ``6``.

    Example:

        >>> glyph = font["uniE050"]
        >>> point1, point2 = glyph[0].points[:2]
        >>> rulers.areAlligned((point1, point2), axis="x", tolerance=3)
        False

    """

    def withinRange(value: int | float, reference: int | float) -> bool:
        # Check if values are within range of each other +/- the tolerance level.
        return value - tolerance <= reference <= value + tolerance

    first, *rest = points
    reference = getattr(first, axis)
    return all(withinRange(getattr(v, axis), reference) for v in rest)


def getGlyphContours(
    glyph: Glyph, includeComponents: bool = True
) -> Generator[RContour]:
    """Return all contours in `glyph`, including component references.

    :param glyph: The :class:`.Glyph` containing the contours to retrieve.
    :param includeComponents: Whether to include any referenced contours in the glyph.
        Defaults to :obj:`True`.

    Example:

        >>> glyph = font["uniE050"]
        >>> rulers.getGlyphContours(glyph)  # doctest: +ELLIPSIS
        <generator object getGlyphContours.<locals>.<genexpr> at 0x...>

    """
    if glyph.components and includeComponents:
        tempGlyph = glyph.copy()
        font = glyph.font
        tempName = "com.smufolib.temp"
        font.insertGlyph(tempGlyph, name=tempName)
        tempAssigned = font[tempName]
        tempAssigned.decompose()
        contours = (c for c in tempAssigned)
        font.removeGlyph(tempName)
        return contours
    return (c for c in glyph)


def getGlyphSegments(
    glyph, types: str | tuple[str, ...] = TYPES, includeComponents: bool = True
) -> Generator[RSegment]:
    """Return all segments in `glyph`, matching given `types`.

    Any segments referenced by components may be included.

    :param glyph: The :class:`.Glyph` containing the segments to retrieve.
    :param types: The :attr:`~fontParts.base.BaseSegment.type` values to include.
        Defaults to ``("line", "curve", "qcurve")``.
    :param includeComponents: Whether to include any referenced contours in the glyph.

    Example:

        >>> glyph = font["uniE050"]
        >>> rulers.getGlyphSegments(glyph)  # doctest: +ELLIPSIS
        <generator object getGlyphSegments.<locals>.<genexpr> at 0x...>

    """
    contours = getGlyphContours(glyph, includeComponents=includeComponents)
    return (s for sts in contours for s in sts if s.type in types or s.type == types)


def getGlyphPoints(
    glyph, types: str | tuple[str, ...] = TYPES, includeComponents: bool = True
) -> Generator[RPoint]:
    """Return all points in `glyph`, matching given `types`.

    Any points referenced by components may be included.

    :param glyph: The :class:`.Glyph` containing the points to retrieve.
    :param types: The :attr:`~fontParts.base.BasePoint.type` values to include.
        Defaults to ``("line", "curve", "qcurve")``.
    :param includeComponents: Whether to include any referenced contours in the glyph.

    Example:

        >>> glyph = font["uniE050"]
        >>> rulers.getGlyphPoints(glyph)  # doctest: +ELLIPSIS
        <generator object getGlyphPoints.<locals>.<genexpr> at 0x...>

    """

    segments = getGlyphSegments(glyph, includeComponents=includeComponents, types=types)
    return (p for pts in segments for p in pts if p.type in types or p.type == types)


def hasHorizontalOffCurve(point: RPoint) -> bool:
    """Check if the given point has a predominantly horizontal off-curve.

    An off-curve control point is considered horizontal if its *x-difference* from the
    on-curve point is greater than its *y-difference*.

    :param point: The on-curve point to check.

    Example:

        >>> glyph = font["uniE260"]
        >>> point = glyph[0].points[0]
        >>> rulers.hasHorizontalOffCurve(point)
        True

    """
    segment = getParentSegment(point)
    if segment and point.type in ("curve", "qcurve"):
        for offCurve in segment.offCurve:
            onX, onY = point.position
            offX, offY = offCurve.position
            xDiff = abs(onX - offX)
            yDiff = abs(onY - offY)
            if xDiff > yDiff:
                return True
    return False


def hasVerticalOffCurve(point: RPoint) -> bool:
    """Check if the given point has a predominantly vertical off-curve.

    An off-curve control point is considered vertical if its *y-difference* from the
    on-curve point is greater than its *x-difference*.

    :param point: The on-curve point to check.

    Example:

        >>> glyph = font["uniE260"]
        >>> point = glyph[0].points[0]
        >>> rulers.hasVerticalOffCurve(point)
        False

    """
    segment = getParentSegment(point)
    if segment and point.type in ("curve", "qcurve"):
        for offCurve in segment.offCurve:
            onX, onY = point.position
            offX, offY = offCurve.position
            xDiff = abs(onX - offX)
            yDiff = abs(onY - offY)
            if xDiff < yDiff:
                return True
    return False


def getParentSegment(point: RPoint) -> RSegment | None:
    """Get the segment which the given point belongs to.

    :param point: The point to find the parent segment for.

    Example:

        >>> glyph = font["uniE050"]
        >>> point = glyph[0].points[0]
        >>> rulers.getParentSegment(point)  # doctest: +ELLIPSIS
        <RSegment line index='3' at ...>

    """
    match = next(
        (s for s in point.contour.segments if point.contour and point in s), None
    )
    return match


def combineBounds(boundsList: list[Bounds]) -> Bounds | None:
    """Combine a list of bounds into one bounding box.

    Example:

        >>> glyph1, glyph2 = font["uniE050"], font["uniE260"]
        >>> boundsList = [glyph1.bounds, glyph2.bounds]
        >>> rulers.combineBounds(boundsList)
        (-50, -634, 648, 1167)

    """
    if not boundsList:
        return None

    xMins, yMins, xMaxs, yMaxs = zip(*boundsList)
    return (min(xMins), min(yMins), max(xMaxs), max(yMaxs))


# ----------
# Dispatcher
# ----------

#: Dispatch the different ruler functions by their :class:`str` name.
DISPATCHER: dict[str, RulerType] = {
    "glyphBoundsHeight": glyphBoundsHeight,
    "glyphBoundsWidth": glyphBoundsWidth,
    "glyphBoundsXMinAbs": glyphBoundsXMinAbs,
    "xDistanceStemToDot": xDistanceStemToDot,
    "xDistanceBetweenContours": xDistanceBetweenContours,
    "xStrokeWidthAtOrigin": xStrokeWidthAtOrigin,
    "yDistanceBetweenContours": yDistanceBetweenContours,
    "yStrokeWidthAtMinimum": yStrokeWidthAtMinimum,
    "wedgeArmStrokeWidth": wedgeArmStrokeWidth,
}
