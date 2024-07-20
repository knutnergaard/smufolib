# pylint: disable=C0114
from __future__ import annotations
from typing import Any
from collections.abc import Generator, Iterable
import operator

# pylint: disable=C0103


def flatten(iterable: Iterable[Any],
            depth: int | None = None
            ) -> Generator:
    """Flatten irregularly nested iterables of any depth.

    :param iterable: The :term:`iterable` to flatten.
    :param depth: The number of levels to flatten. `depth=None` employs
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


def addTuples(*tuples: tuple[int | float, ...]) -> tuple[int | float, ...]:
    r"""Sumize tuple values.

    :param \*tuples: tuples to add.

    Example::

        >>> addTuples((2, 4), (2, 4))
        (4, 8)

    """
    return tuple(map(sum, zip(*tuples)))


def getSummary(docstring: str | None) -> str | None:
    """Get summary line from docstring.

    :param docstring: The docstring from which to get the summary line.

    """
    if docstring is None:
        return None

    return docstring.split('\n', maxsplit=1)[0]


def isFloat(string: str) -> bool:
    """Check if string represents a :class:`float`.

    param string: The string to check.

    """
    if '.' not in string:
        return False
    try:
        float(string)
        return True
    except ValueError:
        return False


def validateClassAttr(obj, attributes: Iterable[str] | None = None) -> bool:
    """Check for class and attribute exsistence.

    Validates object based on its existence and specified attributes.

    :param obj: The object to validate.
    :param attributes: The attribute names to check.

    """
    if isinstance(attributes, str):
        attributes = (attributes,)
    if attributes is None:
        attributes = ()
    getter = operator.attrgetter(*attributes)
    if all(getter(obj)):
        return True
    return False


def doNothing(*args: Any, **kwargs: Any) -> None:
    # pylint: disable=W0613
    r"""Do nothing at all.

    :param \*args: Positional arguments.
    :param \**kwargs: Keyword arguments.

    """


def verbosePrint(message: str, verbose: bool,
                 *args: Any, **kwargs: Any) -> None:
    r"""Print a message if `verbose` is :obj:`True`.

    Behaves like the built-in :func:`print` function, but only prints
    the message if `verbose` is :obj:`True`. If `verbose`
    is :obj:`False`, it does nothing.

    :param message: The message to be printed.
    :param verbose: A flag indicating whether to print the message.
    :param \*args: Additional positional arguments passed to
        the :func:`print` function.
    :param \**kwargs: Additional keyword arguments passed to
        the :func:`print` function.

    """
    if verbose:
        print(message, *args, **kwargs)
    else:
        doNothing(message, *args, **kwargs)
