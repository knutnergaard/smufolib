"""Measurement utilities for calculating glyph geometry.

This module provides functions to retrieve, measure and inspect various parts of glyphs.
It also defines:

- :data:`MAPPING`, the default association between ruler functions and glyphs used for
  calculating :class:`.EngravingDefaults` attribute values.
- :data:`DISPATCHER`, for dynamically executing measurement operations by function name.

"""

from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Callable
from math import dist

from smufolib.utils import converters

if TYPE_CHECKING:  # pragma: no cover
    from fontParts.fontshell.point import RPoint
    from fontParts.fontshell.segment import RSegment
    from smufolib.objects.glyph import Glyph

Bounds = tuple[int | float, int | float, int | float, int | float]
MappingValue = str | int | None
Mapping = dict[str, MappingValue]
Remapping = dict[str, Mapping]
RulerType = Callable[["Glyph"], int | float | None]

TOLERANCE: int | float = 6
TYPES: str | tuple[str, ...] = ("line", "curve", "qcurve")

#: Default mapping of ruler functions and glyphs to engravingDefaults attribute names.
MAPPING: Remapping = {
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

    """
    boundsList = [c.bounds for c in getGlyphContours(glyph)]
    bounds = combineBounds(boundsList)
    if not bounds:
        return None
    return converters.toIntIfWhole(bounds[3] - bounds[1])


def glyphBoundsWidth(glyph: Glyph) -> int | float | None:
    """Return width of the glyph's bounding box.

    :param glyph: Source :class:`.Glyph` of contours to measure.

    """
    boundsList = [c.bounds for c in getGlyphContours(glyph)]
    bounds = combineBounds(boundsList)
    if not bounds:
        return None
    return converters.toIntIfWhole(bounds[2] - bounds[0])


def glyphBoundsXMinAbs(glyph: Glyph) -> int | float | None:
    """Return absolute value of glyph's xMin bound.

    :param glyph: Source :class:`.Glyph` of contours to measure.

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
    """Measure thickness of arm in a wdge-shaped glyph.

    :param glyph: Source :class:`.Glyph` of contours to measure.

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
    """Return :obj:`True` if the specified `points` are aligned on `axis`.

    :param points: The points to check for alignment.
    :param axis: The axis (``"x"`` or ``"y"``) accross which to check for alignment.
    :param tolerance: The tolerance for misalignment to apply in font units.
        Defaults to ``6``.

    """

    def withinRange(value: int | float, reference: int | float) -> bool:
        # Check if values are within range of each other +/- the tolerance level.
        return value - tolerance <= reference <= value + tolerance

    first, *rest = points
    reference = getattr(first, axis)
    return all(withinRange(getattr(v, axis), reference) for v in rest)


def getGlyphContours(glyph: Glyph, includeComponents=True):
    """Return all contours in the glyph, including component references.

    :param glyph: The :class:`.Glyph` containing the contours to retrieve.
    :param includeComponents: Whether to include any referenced contours in the glyph.
        Defaults to :obj:`True`.

    """
    if glyph.components and includeComponents:
        tempGlyph = glyph.copy()
        font = glyph.font
        tempName = "com.smufolib.temp"
        font.insertGlyph(tempGlyph, name=tempName)
        tempAssigned = font[tempName]
        tempAssigned.decompose()
        contours = (c for c in tempAssigned.contours)
        font.removeGlyph(tempName)
        return contours
    return (c for c in glyph.contours)


def getGlyphSegments(
    glyph, types: str | tuple[str, ...] = TYPES, includeComponents=True
):
    """Return all segments in the `glyph` matching given `types`.

    Any segments referenced by components may be included.

    :param glyph: The :class:`.Glyph` containing the segments to retrieve.
    :param types: The :attr:`~fontParts.base.BaseSegment.type` values to include.
        Defaults to ``("line", "curve", "qcurve")``.
    :param includeComponents: Whether to include any referenced contours in the glyph.

    """
    contours = getGlyphContours(glyph, includeComponents=includeComponents)
    return (s for sts in contours for s in sts if s.type in types or s.type == types)


def getGlyphPoints(glyph, types: str | tuple[str, ...] = TYPES, includeComponents=True):
    """Return all points in the `glyph` matching given `types`.

    Any points referenced by components may be included.

    :param glyph: The :class:`.Glyph` containing the points to retrieve.
    :param types: The :attr:`~fontParts.base.BasePoint.type` values to include.
        Defaults to ``("line", "curve", "qcurve")``.
    :param includeComponents: Whether to include any referenced contours in the glyph.

    """

    segments = getGlyphSegments(glyph, includeComponents=includeComponents, types=types)
    return (p for pts in segments for p in pts if p.type in types or p.type == types)


def hasHorizontalOffCurve(point: RPoint) -> bool:
    """Return :obj:`True` if `point` has a predominantly horizontal off-curve.

    An off-curve control point is considered horizontal if its x difference from the
    on-curve point is greater than its y difference.

    :param point: The on-curve point to check.

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
    """Return :obj:`True` if `point` has a predominantly vertical off-curve.

    An off-curve control point is considered vertical if its y difference from the
    on-curve point is greater than its x difference.

    :param point: The on-curve point to check.

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
    """Get the segment which the `point` belongs to.

    :param point: The point to find the parent segment for.

    """
    match = next(
        (s for s in point.contour.segments if point.contour and point in s), None
    )
    return match


def combineBounds(boundsList: list[Bounds]) -> Bounds | None:
    """Combine a list of bounds into one bounding box."""
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
