from __future__ import annotations
from typing import TYPE_CHECKING, Any
from collections.abc import Iterable
import operator

# pylint: disable=invalid-name


def flatten(iterable: Iterable[Any], depth: int = None) -> Iterable[Any]:
    """Flatten irregularly nested iterables of any depth."""
    for item in iterable:
        if (not isinstance(item, Iterable)
                or isinstance(item, (str, bytes)) or depth == 0):
            yield item
        elif depth is None:
            yield from flatten(item)
        else:
            yield from flatten(item, depth - 1)


def addTuples(*tuples) -> tuple[int | float]:
    """Sumize tuple values."""
    return tuple(map(sum, zip(*tuples)))


def isFloat(string: str) -> bool:
    """Check if string is float."""
    if '.' not in string:
        return False
    try:
        float(string)
        return True
    except ValueError:
        return False


def validateClassAttr(obj, attributes: Iterable | None = None) -> bool:
    """Check for class and attribute exsistence.

    Vvalidates object based on its existence and specified attributes.

    :param obj: Object to validate
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
