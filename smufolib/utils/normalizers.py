"""Utilities for normalizing various data types in SMufoLib.

This module extends :mod:`fontParts.base.normalizers` and provides
functions to normalize objects and data related to SMuFL fonts and
metadata requests. It includes normalization for:

    - :class:`.Font` objects
    - :class:`.Smufl` objects and attributes
    - :class:`.EngravingDefaults` objects and attributes
    - :class:`.Request` objects and attributes

These functions ensure that the data adheres to expected formats and
values, handling type validation and normalization as needed.

In addition to the documented functions below, it provides direct access
to the following external normalizers for convenience:

    - :func:`~fontParts.base.normalizers.normalizeBoolean`
    - :func:`~fontParts.base.normalizers.normalizeColor`
    - :func:`~fontParts.base.normalizers.normalizeVisualRounding`
    - :func:`~fontParts.base.normalizers.normalizeGlyph`

"""

from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path

# ruff: noqa: F401
# pylint: disable=W0611
from fontParts.base.normalizers import normalizeInternalObjectType
from fontParts.base.normalizers import normalizeBoolean
from fontParts.base.normalizers import normalizeColor
from fontParts.base.normalizers import normalizeVisualRounding
from fontParts.base.normalizers import normalizeGlyph
from smufolib.utils import error

# ruff: noqa: F401
# pylint: enable=W0611
if TYPE_CHECKING:  # pragma: no cover
    from smufolib.objects.font import Font
    from smufolib.request import Request
    from smufolib.objects.smufl import Smufl
    from smufolib.objects.engravingDefaults import EngravingDefaults

# Type aliases
EngravingDefaultsInput = int | float | tuple[str, ...] | list[str]
EngravingDefaultsReturn = int | float | tuple[str, ...]

# pylint: disable=C0103, C0415


# ----
# Font
# ----


def normalizeFont(value: Font) -> Font:
    """Normalize Font object.

    :param value: The value to normalize.
    :raises TypeError: If `value` is not the accepted type.

    """
    from smufolib.objects.font import Font

    return normalizeInternalObjectType(value, Font, "Font")


# -----
# Smufl
# -----


def normalizeClasses(value: tuple[str, ...] | None) -> tuple[str, ...]:
    """Normalize smufl classes.

    :param value: The value to normalize.
    :raises TypeError: If `value` is not an accepted type.
    :raises ValueError:
        - If any `value` item does not normalize
          with :func:`normalizeSmuflName`.
        - If any `value` items are duplicates.

    """
    if value is None:
        return ()

    objectName = "Smufl.classes"
    error.validateType(value, (tuple, list), objectName)

    for val in value:
        error.validateType(val, str, objectName, items=True)
        for v in val.split("_"):
            normalizeSmuflName(v, items=True)

    duplicates = {v for v in value if value.count(v) > 1}
    if len(duplicates) != 0:
        raise ValueError(
            error.generateErrorMessage("duplicateItems", objectName=objectName)
        )

    return tuple(v for v in value if v)


def normalizeDescription(value: str | None) -> str | None:
    """Normalize smufl descriptions.

    :param value: The value to normalize.
    :raises TypeError: If `value` is not an accepted type.
    :raises ValueError: If `value` is an empty string.

    """
    if value is None:
        return None

    error.validateType(value, (str, type(None)), "Smufl.description")

    if len(value) == 0:
        raise ValueError(
            error.generateErrorMessage("emptyValue", objectName="Smufl.description")
        )

    return value


def normalizeDesignSize(value: int | None) -> int | None:
    """Normalize design size.

    :param value: The value to normalize.
    :raises TypeError: If `value` is not an accepted type.
    :raises ValueError: If `value` is less than ``10``.

    """
    error.validateType(value, (int, type(None)), "Smufl.designSize")

    if value is None:
        return None

    if value < 10:
        raise ValueError(
            error.generateErrorMessage(
                "valueTooLow", objectName="Smufl.designSize", value=10
            )
        )

    return value


def normalizeSizeRange(value: tuple[int, int] | None) -> tuple[int, int] | None:
    """Normalize design size.

    :param value: The value to normalize.
    :raises TypeError: If `value` or it's contents is not an accepted
        type.
    :raises ValueError:
        - If `value` does not contain a value pair.
        - If `value` is not an increasing range.
        - If `value` items do not normalize
          with :func:`normalizeDesignSize`, except not be :obj:`None`.

    """
    if value is None:
        return None

    objectName = "Smufl.sizeRange"

    error.validateType(value, (tuple, list, type(None)), objectName)

    if len(value) != 2:
        raise ValueError(
            error.generateErrorMessage("singleItem", objectName="Smufl.sizeRange")
        )

    start, end = value

    startNormalized = normalizeDesignSize(start)
    endNormalized = normalizeDesignSize(end)

    if start >= end:
        raise ValueError(
            error.generateErrorMessage("nonIncreasingRange", objectName=objectName)
        )

    return startNormalized, endNormalized  # type: ignore


def normalizeSmufl(value: Smufl) -> Smufl:
    """Normalize Smufl object.

    :param value: The value to normalize.
    :raises TypeError: If `value` is not the accepted type.

    """
    from smufolib.objects.smufl import Smufl

    return normalizeInternalObjectType(value, Smufl, "Smufl")


def normalizeSmuflName(value: str | None, items: bool = False) -> str | None:
    """Normalize smufl names.

    :param value: The value to normalize.
    :param items: Whether to normalize `value` items rather than `value`
        itself. Defaults to :obj:`False`.
    :raises TypeError: If `value` is not an accepted type.
    :raises ValueError:
        - If `value` is an empty string.
        - If `value` is value contains non-alphanumeric characters.
        - If `value` does not start with a lowercase letter or number.

    """
    if value is None:
        return None

    objectName = "Smufl.name"
    if items:
        objectName = "Smufl.classes"

    error.validateType(value, (str, type(None)), objectName)

    if not value:
        template = "emptyValueItems" if items else "emptyValue"
        raise ValueError(error.generateErrorMessage(template, objectName=objectName))

    for val in value:
        if not val.isalnum():
            template = "alphanumericValueItems" if items else "alphanumericValue"
            raise ValueError(
                error.generateErrorMessage(template, objectName=objectName)
            )

    if value[0].isupper():
        template = (
            "invalidInitialItemsCharacter" if items else "invalidInitialCharacter"
        )
        raise ValueError(error.generateErrorMessage(template, objectName=objectName))

    return value


# ------------------
# Engraving defaults
# ------------------


def normalizeEngravingDefaults(value: EngravingDefaults) -> EngravingDefaults:
    """Normalize EngravingDefaults object.

    :param value: The value to normalize.
    :raises TypeError: If `value` is not the accepted type.

    """
    from smufolib.objects.engravingDefaults import EngravingDefaults

    return normalizeInternalObjectType(value, EngravingDefaults, "EngravingDefaults")


def normalizeEngravingDefaultsAttr(
    name: str, value: EngravingDefaultsInput | None
) -> EngravingDefaultsReturn | None:
    """Normalize engraving defaults attribute value based on name.

    :param name: The name of the attribute to normalize.
    :param value: The value to normalize.
    :raises TypeError: If any parameter value is not an accepted type.
    :raises AttributeError: If name is not a
        valid :class:`.EngravingDefaults` attribute name.
    :raises ValueError: If  ``'name=textFontFamily'`` and `value` is not
        a :class:`str` or empty.

    """
    from smufolib.objects.engravingDefaults import ENGRAVING_DEFAULTS_KEYS

    if not isinstance(name, str):
        raise TypeError(
            error.generateTypeError(value=name, validTypes=str, objectName="name")
        )

    className = "EngravingDefaults"
    if name not in ENGRAVING_DEFAULTS_KEYS:
        raise AttributeError(
            error.generateErrorMessage(
                "attributeError", objectName=className, attribute=name
            )
        )

    if value is None:
        return () if name == "textFontFamily" else None

    objectName = f"{className}.{name}"
    if name == "textFontFamily":
        if not isinstance(value, (tuple, list)):
            raise TypeError(
                error.generateTypeError(
                    value=value, validTypes=(tuple, list), objectName=objectName
                )
            )

        value = _normalizeStringTuple(objectName, value)

    elif not isinstance(value, (int, float)):
        raise TypeError(
            error.generateTypeError(
                value=value, validTypes=(int, float), objectName=objectName
            )
        )

    return value


def _normalizeStringTuple(
    objectName: str, value: tuple[str, ...] | list[str]
) -> tuple[str, ...]:
    # Normalize string tuple.
    error.validateType(value, (tuple, list), objectName)

    for val in value:
        error.validateType(val, str, objectName, items=True)
        if not val:
            raise ValueError(
                error.generateErrorMessage("emptyValueItems", objectName=objectName)
            )

    return tuple(value)


# -------
# Request
# -------


def normalizeRequest(value: Request) -> Request:
    """Normalize Request object.

    :param value: The value to normalize.
    :raises TypeError: If `value` is not the accepted type.

    """
    from smufolib.request import Request

    return normalizeInternalObjectType(value, Request, "Request")


def normalizeRequestPath(value: Path | str | None, parameter: str) -> str | None:
    """Normalize Request path.

    Relative paths are resolved automatically.

    :param value: The value to normalize.
    :param parameter: The name of the parameter being validated.
    :raises TypeError: If `value` is not the accepted type.

    """
    if value is None:
        return None
    error.validateType(value, (str, Path), parameter)
    if str(value).startswith("."):
        return str(Path(value).resolve())
    return str(value)
