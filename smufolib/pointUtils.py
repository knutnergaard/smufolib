from __future__ import annotations
from typing import TYPE_CHECKING, NamedTuple
import itertools

from smufolib import stdUtils

if TYPE_CHECKING:
    from fontParts.fontshell import RComponent
    from fontParts.fontshell import RContour
    from smufolib.objects.glyph import Glyph


# pylint: disable=invalid-name, too-many-arguments


class Point(NamedTuple):
    """Named tuple for point values."""
    type: str
    position: Position
    contourIndex: int


class Position(NamedTuple):
    """Named tuple for position values."""
    x: int | float
    y: int | float


def getPoints(glyph: Glyph,
              types: str | tuple[str] = ('line', 'curve', 'qcurve')
              ) -> tuple[NamedTuple]:
    """Get tuple of points for a glyph.

    :param glyph: The :class:`Glyph` object from which to get the
        points.
    :param types: The types of points to get as a :class:`tuple` of
     ``'line'``, ``'curve'`` and/or ``'qcurve'``. Defaults to a tuple
     of all three types.

    """
    points = (getContourPoints(c, types) for c in glyph)
    if glyph.components:
        points = itertools.chain(
            points, (getCompositePoints(c, types) for c in glyph.components))
    return tuple(stdUtils.flatten(points, 1))


def getContourPoints(contour: RContour,
                     types: str | tuple[str] = ('line', 'curve', 'qcurve')
                     ) -> tuple[NamedTuple]:
    """Get tuple of points for all glyph contours.

    :param glyph: The :class:`Glyph` object from which to get the
        points.
    :param types: The types of points to get as a :class:`tuple` of
     ``'line'``, ``'curve'`` and/or ``'qcurve'``. Defaults to a tuple
     of all three types.

     """
    rawPoints = stdUtils.flatten(contour)
    return tuple(Point(p.type, Position(*p.position), p.contour.index)
                 for p in rawPoints if p.type in types)


def getCompositePoints(component: RComponent,
                       types: str | tuple[str] = ('line', 'curve', 'qcurve')
                       ) -> tuple[str, tuple[int], int]:
    """Get points and offset position from glyph component.

    :param glyph: The :class:`Glyph` object from which to get the
        points.
    :param types: The types of points to get as a :class:`tuple` of
     ``'line'``, ``'curve'`` and/or ``'qcurve'``. Defaults to a tuple
     of all three types.

     """
    baseGlyph = component.font[component.baseGlyph]
    rawPoints = stdUtils.flatten(baseGlyph.contours)
    offset, index = component.offset, component.index
    return tuple(Point(
        p.type, Position(*stdUtils.addTuples(p.position, offset)),
        index) for p in rawPoints if p.type in types)
