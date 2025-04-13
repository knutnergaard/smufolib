"""Miscellaneous general-purpose utility functions.

This module provides a set of utility functions for various common
tasks, including flattening nested iterables, summing tuples, and
extracting summary lines from docstrings. It also includes functions for
validating class attributes and string representations of floats,
printing verbose messages, as well as a a no-op function for
placeholder purposes.

"""

import operator
from typing import Any
from collections.abc import Generator, Iterable

# pylint: disable=C0103


def flatten(iterable: Iterable[Any], depth: int | None = None) -> Generator:
    """Flatten irregularly nested iterables of any depth.

    :param iterable: The :term:`iterable` to flatten.
    :param depth: The number of levels to flatten. `depth=None` employs
        maximum flattening. Defaults to :obj:`None`.

    :return: A generator yielding the flattened elements.

    Examples::

        >>> list(flatten([1, [2, [3, [4, 5]]]], depth=2))
        [1, 2, 3, [4, 5]]

        >>> list(flatten([1, [2, [3, [4, [5]]]]], depth=None))
        [1, 2, 3, 4, 5]

    """
    for item in iterable:
        if (
            not isinstance(item, Iterable)
            or isinstance(item, (str, bytes))
            or depth == 0
        ):
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
    '''Extract the summary line from a docstring.

    :param docstring: The docstring from which to get the summary line.

    Example::

        >>> def showcaseGetSummary():
        ...     """Provide an example for the `getSummary()` function.
        ...
        ...     This function provides an example to show how to
        ...     extract a summary line from a docstring.
        ...
        ...     """
        ...
        >>> docstring = showcaseGetSummary.__doc__
        >>> getSummary(docstring)
        "Give example for `getSummary()` function."

    '''
    if docstring is None:
        return None

    return docstring.split("\n", maxsplit=1)[0]


def isFloat(string: str) -> bool:
    """Check if string represents a :class:`float`.

    :param string: The string to check.

    Examples::

        >>> isFloat("3.14")
        True

        >>> isFloat("314")
        False

    """
    if "." not in string:
        return False
    try:
        float(string)
        return True
    except ValueError:
        return False


def validateAttr(obj, attributes: Iterable[str] | None = None) -> bool:
    """Validate `obj` based on whether the given attributes have been set.

    This function returns :obj:`False` if any given attribute is not :obj:`None`,
    otherwise itreturns :obj:`True`. It supports validation of nested
    attributes, e.g.: ``"attr1.attr2.attr3"``.

    :param obj: The object to validate.
    :param attributes: The attribute names to check.

    Example::

        >>> class MyClass:
        ...     def __init__(self):
        ...         self.attr1 = 1
        ...         self.attr2 = None
        ...         self.attr3 = False
        ...
        >>> obj = MyClass()
        >>> validateAttr(obj, 'attr1')
        True
        >>> validateAttr(obj, 'attr2')
        False
        >>> validateAttr(obj, 'attr3')
        True
        >>> validateAttr(obj, ['attr1', 'attr2'])
        False

    """
    if not attributes:
        return False

    if isinstance(attributes, str):
        attributes = (attributes,)

    return all(operator.attrgetter(attr)(obj) is not None for attr in attributes)


def doNothing(*args: Any, **kwargs: Any) -> None:
    # pylint: disable=W0613
    r"""Do nothing at all.

    This function accepts any arguments but does nothing with them.

    :param \*args: Positional arguments.
    :param \**kwargs: Keyword arguments.

    Example::

        >>> doNothing(1, 2, 3)
        >>> doNothing(a=1, b=2)

    """


def verbosePrint(message: str, verbose: bool, *args: Any, **kwargs: Any) -> None:
    r"""Print a message if `verbose` is :obj:`True`.

    This function behaves like the built-in :func:`print` function, but
    only prints the message if `verbose` is :obj:`True`. If `verbose`
    is :obj:`False`, it does nothing.

    :param message: The message to be printed.
    :param verbose: A flag indicating whether to print the message.
    :param \*args: Additional positional arguments passed to
        the :func:`print` function.
    :param \**kwargs: Additional keyword arguments passed to
        the :func:`print` function.

    Example::

        >>> verbosePrint('Hello, world!', True)
        Hello, world!
        >>> verbosePrint('Hello, world!', False)
        >>> verbosePrint('Hello, {}!', True, 'Alice')
        Hello, Alice!

    """
    if verbose:
        print(message, *args, **kwargs)
    else:
        doNothing(message, *args, **kwargs)
