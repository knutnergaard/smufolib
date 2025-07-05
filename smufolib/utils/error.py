"""Utility functions for error message generation and type validation.

This module provides functions to generate and validate error messages,
check types, and suggest corrections for invalid values. It includes
a dictionary of error message templates to ensure streamlined and
consistent error reporting.

To import the module:

    >>> from smufolib import error

"""

from __future__ import annotations
from types import UnionType
from typing import get_args, Any
import difflib

from smufolib.utils._annotations import ErrorKey

# pylint: disable=C0103

#: Dictionary of error message templates.
ERROR_TEMPLATES: dict[str, str] = {
    "alphanumericValue": "The value for {objectName!r} must be alphanumeric",
    "alphanumericValueItems": "Value items for {objectName!r} must be alphanumeric",
    "argumentConflict": "The option '{key}' is already added as positional argument or flag",
    "attributeError": "{objectName!r} has no attribute {attribute!r}",
    "contextualAttributeError": "The attribute {attribute!r} is not available when {context}",
    "contextualSetAttributeError": "Cannot set attribute {attribute!r} when {context}",
    "contextualTypeError": "Expected {objectName!r} to be of type {validTypes} when {context}, but got {valueType}",
    "contextualItemsTypeError": "Items in {objectName!r} must be {validTypes} when {context}, not {valueType}",
    "deprecated": "{objectName!r} is deprecated and will be removed in the next version of SMufoLib (after {version})",
    "deprecatedReplacement": "Use {replacement!r} instead",
    "duplicateFlags": "Arguments {argument1!r} and {argument2!r} have duplicate short flag: {flag}",
    "duplicateAttributeValue": "The value {value!r} for {attribute!r} is already assigned to another {objectName} instance: {conflictingInstance!r}",
    "duplicateItems": "Items in {objectName!r} cannot be duplicates",
    "emptyValue": "The value for {objectName!r} cannot be empty",
    "emptyValueItems": "Value items for {objectName!r} cannot be empty",
    "fileNotFound": "The file or directory for {objectName!r} does not exist",
    "invalidFormat": "The value for {objectName!r} is not correctly formatted",
    "invalidInitialCharacter": "The value for {objectName!r} must start with a lowercase letter or number",
    "invalidInitialItemsCharacter": "Value items for {objectName!r} must start with a lowercase letter or number",
    "itemsTypeError": "Items in {objectName!r} must be {validTypes}, not {valueType}",
    "itemsValueError": "Invalid value for item in {objectName!r}: {value!r}",
    "missingDependency": "Cannot set {objectName!r} because {dependency!r} is None",
    "missingExtension": "The value for {objectName!r} must have a {extension!r} extension",
    "missingGlyph": "No SMuFL glyph named {name!r}",
    "missingValue": "Required values for {objectName!r} are missing",
    "nonIncreasingRange": "The values in {objectName!r} must form an increasing range",
    "notImplementedError": "The {objectName!r} subclass does not implement this method",
    "numericValue": "The value for {objectName!r} must be numeric",
    "overlappingRange": "Range '{name}' ({start}-{end}) overlaps with an existing range",
    "permissionError": "Permission denied: {context}",
    "recommendScript": "Consider running the script {scriptName!r} before the current process",
    "serializationError": "Error serializing JSON data or writing to the file",
    "singleItem": "{objectName!r} must contain a value pair",
    "suggestion": "Did you mean {suggestion!r}?",
    "typeError": "Expected {objectName!r} to be of type {validTypes}, but got {valueType}",
    "unicodeOutOfRange": "The value for {objectName!r} is outside the Unicode range {start}-{end}",
    "urlError": "Could not connect to URL: {url!r}",
    "valueError": "Invalid value for {objectName!r}: {value!r}",
    "valueTooHigh": "The value for {objectName!r} must be {value!r} or lower",
    "valueTooLow": "The value for {objectName!r} must be {value!r} or higher",
}


class URLWarning(Warning):
    """URL connection failure warning."""


def generateErrorMessage(
    *templateNames: ErrorKey, string: str | None = None, **kwargs
) -> str:
    r"""Generate an error message from a template and keyword arguments.

    The `templateNames` and `string` will be concatenated in order.

    :param \*templateNames: The error message template string, which
        should contain placeholders for keyword arguments.
    :param string: An additional message string to include.
        Defaults to :obj:`None`
    :param \**kwargs: Arbitrary keyword arguments corresponding to the
        placeholders in the template string.
    :raises KeyError: If a placeholder in the template does not have a
        corresponding keyword argument.

    Examples:

        >>> error.generateErrorMessage("alphanumericValue", objectName="unicode")
        "The value for 'unicode' must be alphanumeric"

        >>> error.generateErrorMessage(
        ...     "typeError", objectName="index", validTypes="int", valueType="str"
        ...     )
        "Expected 'index' to be of type int, but got str"

        >>> error.generateErrorMessage(
        ...     "urlError", string="Please try again", url="some/url.com"
        ...     )
        "Could not connect to URL: 'some/url.com'. Please try again"

    """
    messages = [ERROR_TEMPLATES[n].format(**kwargs) for n in templateNames]
    if string:
        messages.append(string)
    return ". ".join(messages)


def generateTypeError(
    value: Any,
    validTypes: type | tuple[type, ...],
    objectName: str,
    context: str | None = None,
    items: bool = False,
) -> str:
    """Generate a :class:`TypeError` message.

    This function generates an error message based on the number of
    valid types. By default, the message is generated from
    :obj:`ERROR_TEMPLATES`:``"typeError"``.

    If `context` in not :obj:`None` (or empty) and `items`
    is :obj:`False`, :obj:`ERROR_TEMPLATES`:``"contextualTypeError"``
    is used. If `items` is :obj:`True` and `context` is :obj:`None`,
    :obj:`ERROR_TEMPLATES`:``"itemsTypeError"`` is used. If both
    `context` is not :obj:`None` and `items` is :obj:`True`,
    :obj:`ERROR_TEMPLATES`:``"contextualItemsTypeError"`` is used.

    :param value: The value to be validated.
    :param validTypes: A :class:`tuple` or :class:`list` of valid types.
    :param objectName: The name of the object being validated.
    :param context: Additional substring for contextual type errors.
        Defaults to :obj:`None`
    :param items: Whether to use items-specific template. Defaults
        to :obj:`False`.
    :raises TypeError: If `value` does not match any of the valid
        types.
    :raises ValueError: If `items` is :obj:`True` and `value` is not
        an iterable.

    Examples:

        >>> error.generateTypeError(123, (str,), "path")
        "Expected 'path' to be of type str, but got int"

        >>> from pathlib import Path
        >>> error.generateTypeError(123, (str, Path), "path")
        "Expected 'path' to be of type str or Path, but got int"

        >>> from smufolib import Request
        >>> error.generateTypeError(123, (str, Path, Request), "path")
        "Expected 'path' to be of type str, Path or Request, but got int"

    """
    typeNames = _listTypes(validTypes)
    valueType = type(value).__name__

    kwargs = {
        "validTypes": typeNames,
        "objectName": objectName,
        "valueType": valueType,
    }

    if context:
        template: ErrorKey = (
            "contextualItemsTypeError" if items else "contextualTypeError"
        )
        kwargs["context"] = context
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

    Examples:

        >>> try:
        ...     error.validateType(123, str, "glyphName")
        ... except TypeError as e:
        ...     print(e)
        Expected 'glyphName' to be of type str, but got int

        >>> myList = ["uniE000", 1]
        >>> for item in myList:
        ...     try:
        ...         error.validateType(item, str, "myList", items=True)
        ...     except ValueError as e:
        ...         print(e)
        Items in 'myList' must be str, not int

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
    """Validate value and suggests a valid close match.

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

    Example:

        >>> try:
        ...     error.suggestValue(
        ...         "spiltStemUpSE", ["splitStemUpSE", "splitStemUpSW"],
        ...         "anchorName", cutoff=0.5)
        ... except ValueError as e:
        ...     print(e)
        Invalid value for 'anchorName': 'spiltStemUpSE'. Did you mean 'splitStemUpSE'?

    """
    if value in possibilities:
        return value
    closeMatches = difflib.get_close_matches(value, possibilities, 1, cutoff)
    if closeMatches:
        suggestion = closeMatches[0]
        template: ErrorKey = "itemsValueError" if items else "valueError"
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
