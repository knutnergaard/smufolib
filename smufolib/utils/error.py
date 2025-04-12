"""Utility functions for error message generation and type validation.

This module provides functions to generate and validate error messages,
check types, and suggest corrections for invalid values. It includes
a dictionary of error message templates to ensure streamlined and
consistent error reporting.

"""

from __future__ import annotations
from types import UnionType
from typing import Any, get_args
import difflib

# pylint: disable=C0103

#: Dictionary of error message templates.
ERROR_TEMPLATES: dict[str, str] = {
    "alphanumericValue": "The value for '{objectName}' must be alphanumeric.",
    "alphanumericValueItems": "Value items for '{objectName}' must be alphanumeric.",
    "argumentConflict": "The option '{key}' is already added as positional argument or flag.",
    "attributeError": "'{objectName}' has no attribute '{attribute}'.",
    "dependentTypeError": "Expected '{objectName}' to be of type {validTypes} when {dependencyInfo}, but got {value}.",
    "dependentItemsTypeError": "Items in '{objectName}' must be {validTypes} when {dependencyInfo}, not {value}.",
    "duplicateFlags": "Arguments '{argument1}' and '{argument2}' have duplicate short flag: {flag}.",
    "duplicateItems": "Items in '{objectName}' cannot be duplicates.",
    "emptyValue": "The value for '{objectName}' cannot be empty.",
    "emptyValueItems": "Value items for '{objectName}' cannot be empty.",
    "fileNotFound": "The file or directory for '{objectName}' does not exist.",
    "invalidFormat": "The value for '{objectName}' is not correctly formatted.",
    "invalidInitialCharacter": "The value for '{objectName}' must start with a lowercase letter or number.",
    "invalidInitialItemsCharacter": "Value items for '{objectName}' must start with a lowercase letter or number.",
    "itemsTypeError": "Items in '{objectName}' must be {validTypes}, not {value}.",
    "itemsValueError": "Invalid value for item in '{objectName}': {value}.",
    "missingExtension": "The value for '{objectName}' must have a {extension} extension.",
    "missingDependencyError": "Cannot set '{objectName}' because '{dependency}' is None.",
    "missingValue": "Required values for '{objectName}' are missing.",
    "nonIncreasingRange": "The values in '{objectName}' must form an increasing range.",
    "notImplementedError": "The '{objectName}' subclass does not implement this method.",
    "numericValue": "The value for '{objectName}' must be numeric.",
    "recommendScript": "Consider running the script '{scriptName}' before the current process.",
    "serializationError": "Error serializing JSON data or writing to the file.",
    "singleItem": "'{objectName}' must contain a value pair.",
    "suggestion": "Did you mean '{suggestion}'?",
    "typeError": "Expected '{objectName}' to be of type {validTypes}, but got {value}.",
    "unicodeOutOfRange": "The value for '{objectName}' is outside the Unicode range (U+0000 – U+10FFFF).",
    "urlError": "Could not connect to URL: {url}.",
    "valueError": "Invalid value for '{objectName}': {value}.",
    "valueTooHigh": "The value for '{objectName}' must be {value} or lower.",
    "valueTooLow": "The value for '{objectName}' must be {value} or higher.",
}


class URLWarning(Warning):
    """URL connection failure warning."""


def generateErrorMessage(*templateNames: str, **kwargs) -> str:
    """Generate an error message from a template and keyword arguments.

    :param errorTemplate: The error message template string, which
        should contain placeholders for keyword arguments.
    :param kwargs: Arbitrary keyword arguments corresponding to the
        placeholders in the template string.
    :raises KeyError: If a placeholder in the template does not have a
        corresponding keyword argument.

    Example::

        >>> generateErrorMessage('alphanumericValue', objectName='unicode')
        "The value for 'unicode' must be alphanumeric."

        >>> generateErrorMessage('typeError', objectName='index', validTypes='int', value='str')
        "Expected 'index' to be of type int, but got str."

    """
    messages = [ERROR_TEMPLATES[n].format(**kwargs) for n in templateNames]
    return " ".join(messages)


def generateTypeError(
    value: Any,
    validTypes: type | tuple[type, ...] | UnionType,
    objectName: str,
    dependencyInfo: str | None = None,
    items: bool = False,
) -> str:
    """Generate a :class:`TypeError` message.

    This function generates an error message based on the number of
    valid types. By default, the message is generated from
    :obj:`ERROR_TEMPLATES`:``'typeError'``.

    If `dependencyInfo` in not :obj:`None` (or empty) and `items`
    is :obj:`False`, :obj:`ERROR_TEMPLATES`:``'dependentTypeError'``
    is used. If `items` is :obj:`True` and `dependencyInfo` is :obj:`None`,
    :obj:`ERROR_TEMPLATES`:``'itemsTypeError'`` is used. If both
    `dependencyInfo` is not :obj:`None` and `items` is :obj:`True`,
    :obj:`ERROR_TEMPLATES`:``'dependentItemsTypeError'`` is used.

    :param value: The value to be validated.
    :param validTypes: A :class:`tuple` or :class:`list` of valid types.
    :param objectName: The name of the object being validated.
    :param dependencyInfo: Additional substring for dependent type errors.
        template. Defaults to :obj:`None`
    :param items: Whether to use items-specific template. Defaults
        to :obj:`False`.
    :raises TypeError: If `value` does not match any of the valid
        types.
    :raises ValueError: If `items` is :obj:`True` and `value` is not
        an iterable.

    Example::

        >>> generateTypeError(123, (str,), 'path')
        Expected 'path' to be of type str, but got int.

        >>> generateTypeError(123, (str, Path), 'path')
        Expected 'path' to be of type str or Path, but got int.

        >>> generateTypeError(123, (str, Path, Request), 'path')
        Expected 'path' to be of type str, Path or Request, but got int.

    """

    typeNames = _listTypes(validTypes)
    valueType = type(value).__name__

    kwargs = {
        "validTypes": typeNames,
        "objectName": objectName,
        "value": valueType,
    }

    if items and dependencyInfo:
        template = "dependentItemsTypeError"
        kwargs["dependencyInfo"] = dependencyInfo
    elif dependencyInfo:
        template = "dependentTypeError"
        kwargs["dependencyInfo"] = dependencyInfo
    elif items:
        template = "itemsTypeError"
    else:
        template = "typeError"

    return generateErrorMessage(template, **kwargs)


def validateType(
    value: Any,
    validTypes: type | tuple[type, ...] | UnionType,
    objectName: str,
    items=False,
) -> None:
    """Validate if a value matches any of the valid types.

    :param value: The value to be validated.
    :param validTypes: A single valid type or :class:`tuple` of valid
        types.
    :param objectName: The name of the object being validated.
    :param items: Whether to validate `value` items rather than `value`
        itself. Defaults to :obj:`False`.
    :raises TypeError: If `value` does not match any of the valid
        types.
    :raises ValueError: If  `items` is :obj:`True` and any `value` item
        does not match any of the valid types.

    Example::

        >>> validateType(123, str, 'glyphName')
        Traceback (most recent call last):
        ...
        TypeError: Expected 'glyphName' to be of type str, but got int.

        >>> for item in ['uniE000', 1]:
        ...    validateType(item, str, 'glyphNames', items=True)
        Traceback (most recent call last):
        ...
        ValueError: Items in 'glyphNames' must be str, not int.

    """
    if isinstance(validTypes, type):
        validTypes = (validTypes,)

    elif isinstance(validTypes, UnionType):
        validTypes = get_args(validTypes)

    if not isinstance(value, validTypes):
        if items:
            raise ValueError(
                generateTypeError(value, validTypes, objectName, items=items)
            )
        else:
            raise TypeError(generateTypeError(value, validTypes, objectName))


def suggestValue(
    value: str,
    possibilities: list[str] | tuple[str, ...],
    objectName: str,
    cutoff: float = 0.6,
    items=False,
) -> str:
    """Validate value and uggests a valid close match.

    If `items` is :obj:`True`, an alternate error message template is
    used to validate the values of items within an :term:`iterable`
    value rather than the value itself.

    :param value: The value to be validated.
    :param possibilities: A list of valid possibilities for the value.
    :param objectName: The name of the object being validated.
    :param cutoff: A float value representing the cutoff threshold for
        similarity matches. Defaults to ``0.6``.
    :param items: Whether to use items-specific template. Defaults
        to :obj:`False`.
    :raises ValueError: If the provided value is not found in
        `possibilities` or if `items` is :obj:`True` and `value` is
        not an iterable.

    Example::

        >>> suggestValue('spiltStemUpSE', ['splitStemUpSE', 'splitStemUpSW'],
        ... 'anchorName', cutoff=0.5)
        "Invalid value for 'anchorName': spiltStemUpSE. Did you mean 'splitStemUpSE'?"

    """
    if value in possibilities:
        return value
    closeMatches = difflib.get_close_matches(value, possibilities, 1, cutoff)
    if closeMatches:
        suggestion = closeMatches[0]
        template = "itemsValueError" if items else "valueError"
        raise ValueError(
            generateErrorMessage(
                template,
                "suggestion",
                objectName=objectName,
                value=value,
                suggestion=suggestion,
            )
        )

    raise ValueError(
        generateErrorMessage("valueError", objectName=objectName, value=value)
    )


def _listTypes(types: type | tuple[type, ...] | UnionType) -> str:
    # Represent a series of object type names as a string.

    if isinstance(types, type):
        types = (types,)

    elif isinstance(types, UnionType):
        types = get_args(types)

    if len(types) > 1:
        typeNames = (
            ", ".join(t.__name__ for t in types[:-1]) + f" or {types[-1].__name__}"
        )
    else:
        typeNames = types[0].__name__
    return typeNames
