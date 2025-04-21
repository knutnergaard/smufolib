from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Callable

from smufolib.utils import converters, pointUtils

if TYPE_CHECKING:
    from fontParts.fontshell.point import RPoint
    from smufolib.objects.glyph import Glyph

MappingValue = str | int | None
Mapping = dict[str, MappingValue]
Remapping = dict[str, Mapping]
RulerType = (
    Callable[["Glyph"], int | float | None]
    | Callable[["Glyph", int], int | float | None]
)

MARGIN_OF_ERROR = 6
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


# ----------
# Dispatcher
# ----------

DISPATCHER: dict[str, RulerType] = {
    "boundsHeight": boundsHeight,
    "boundsLeft": boundsLeft,
    "stemDot": stemDot,
    "xInner": xInner,
    "xOrigin": xOrigin,
    "yInner": yInner,
    "yMinimum": yMinimum,
}
