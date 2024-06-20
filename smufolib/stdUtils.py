from __future__ import annotations
from typing import TYPE_CHECKING, Any
from collections.abc import Iterable
import operator

# pylint: disable=invalid-name


def flatten(iterable: Iterable[Any], depth: int = None) -> Iterable[Any]:
    """Flatten irregularly nested iterables of any depth.

    :param iterable: iterable to flatten.
    :param debt: number of levels to flatten. ``debt=None`` employs
        maximum flattening. Defaults to :obj:`None`.

    """
    for item in iterable:
        if (not isinstance(item, Iterable)
                or isinstance(item, (str, bytes)) or depth == 0):
            yield item
        elif depth is None:
            yield from flatten(item)
        else:
            yield from flatten(item, depth - 1)


def addTuples(*tuples) -> tuple[int | float]:
    r"""Sumize tuple values.

    :param\*tubles: tuples to add.

    Example::

        >>> addTuples((2, 4), (2, 4))
        (4, 8)

    """
    return tuple(map(sum, zip(*tuples)))


def isFloat(string: str) -> bool:
    """Check if string represents a :class:`float`.

    param string: string to check.

    """
    if '.' not in string:
        return False
    try:
        float(string)
        return True
    except ValueError:
        return False


def validateClassAttr(obj, attributes: Iterable | None = None) -> bool:
    """Check for class and attribute exsistence.

    Validates object based on its existence and specified attributes.

    :param obj: Object to validate.
    :param attributes: Attribute names to check.

    """
    try:
        getter = operator.attrgetter(*attributes)
        if isinstance(attributes, str):
            getter = operator.attrgetter(attributes)
        if all(getter(obj)):
            return True
        return False
    except TypeError as exc:
        raise TypeError("Attributes must be iterable.") from exc
