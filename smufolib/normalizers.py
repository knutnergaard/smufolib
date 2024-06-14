from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path


from fontParts.base.normalizers import normalizeBoolean  # pylint: disable=unused-import
from fontParts.base.normalizers import normalizeColor  # pylint: disable=unused-import
from fontParts.base.normalizers import normalizeInternalObjectType  # pylint: disable=unused-import
from fontParts.base.normalizers import normalizeVisualRounding  # pylint: disable=unused-import
from fontParts.base.normalizers import normalizeGlyph  # pylint: disable=unused-import

if TYPE_CHECKING:
    from smufolib.objects.font import Font
    from smufolib.request import Request
    from smufolib.objects.smufl import Smufl
    from smufolib.objects.engravingDefaults import EngravingDefaults

# pylint: disable=C0103, C0415


# ----
# Font
# ----

def normalizeFont(value: Font) -> Font:
    """Normalize Font object.

    :param value: The value to normalize.
    :raises TypeError: if ``value`` is not the accepted type.

    """
    from smufolib.objects.font import Font
    return normalizeInternalObjectType(value, Font, "Font object")


# -----
# Smufl
# -----

def normalizeClasses(value: tuple[str, ...] | list[str] | None
                     ) -> tuple[str] | None:
    """Normalize smufl classes.

    :param value: The value to normalize.
    :raises TypeError: if ``value`` is not an accepted type.
    :raises ValueError:
        - if any ``value`` item does not normalize.
          with :func:`normalizeSmuflName`.
        - if any ``value`` item is :obj:`None`.
        - if any ``value`` items are duplicates.

    """
    if value is None:
        return None
    if not isinstance(value, (tuple, list)):
        raise TypeError(
            f"Classes must be tuple, list or None, not {type(value).__name__}.")

    for val in value:
        if val is None:
            raise ValueError("Class names cannot be None.")
        for v in val.split('_'):
            normalizeSmuflName(v)

    duplicates = {v for v in value if value.count(v) > 1}
    if len(duplicates) != 0:
        raise ValueError(
            "Duplicate class names are not allowed. Class "
            f"name(s) '{','.join(duplicates)}' are duplicate.")
    return tuple(v for v in value if v)


def normalizeDescription(value: str | None) -> str | None:
    """Normalize smufl descriptions.

    :param value: The value to normalize.
    :raises TypeError: if ``value`` is not an accepted type.
    :raises ValueError: if ``value`` is an empty string.

    """
    if value is None:
        return None
    try:
        if len(value) == 0:
            raise ValueError("The description is empty.")
        return value
    except TypeError as exc:
        raise TypeError("Descriptions must be strings or None, "
                        f"not {type(value).__name__}.") from exc


def normalizeDesignSize(value: int | None) -> int | None:
    """Normalize design size.

    :param value: The value to normalize.
    :raises TypeError: if ``value`` is not an accepted type.
    :raises ValueError: if ``value`` is less than 10.

    """
    if value is None:
        return None
    try:
        if value < 10:
            raise ValueError("Design size must not be less than 10.")
        return value
    except TypeError as exc:
        raise TypeError("Design size must be an integer or None, "
                        f"not {type(value).__name__}.") from exc


def normalizeSizeRange(value: tuple[int, int] | list[int] | None
                       ) -> tuple[int, int] | None:
    """Normalize design size.

    :param value: The value to normalize.
    :raises TypeError: if ``value`` is not an accepted type.
    :raises ValueError:
        - if ``value`` does not contain a value pair.
        - if ``value`` is not an increasing range.
        - if ``value`` items do not normalize
          with :func:`normalizeDesignSize`, except not be :obj:`None`.

    """
    if value is None:
        return None
    try:
        length = len(value)
        if length != 2:
            raise ValueError(f"Size range must be of length 2, not {length}.")
        start, end = value
        if start >= end:
            raise ValueError("Size range values must be an increasing range.")
        return tuple(normalizeDesignSize(start), normalizeDesignSize(end))
    except TypeError as exc:
        raise TypeError(f"Size range must be a list or None, "
                        f"not {type(value).__name__}.") from exc


def normalizeSmufl(value: Smufl) -> Smufl:
    """Normalize Smufl object.

    :param value: The value to normalize.
    :raises TypeError: if ``value`` is not the accepted type.

    """
    from smufolib.objects.smufl import Smufl
    return normalizeInternalObjectType(value, Smufl, "Smufl object")


def normalizeSmuflName(value: str | None) -> str | None:
    """Normalize smufl names.

    :param value: The value to normalize.
    :raises TypeError: if ``value`` is not an accepted type.
    :raises ValueError:
        - if ``value`` is an empty string.
        - if ``value`` is value contains non-alphanumeric characters.
        - if ``value`` does not start with a lowercase letter or number.

    """
    if value is None:
        return None
    try:
        if len(value) == 0:
            raise ValueError("The name is empty.")
        for val in value:
            if not val.isalnum():
                raise ValueError(f"The name '{value}' contains "
                                 f"an invalid character: '{val}'.")
        if value[0].isupper():
            raise ValueError(
                "Names must start with a lowercase letter or number.")
        return value
    except TypeError as exc:
        raise TypeError("Names must be str or None, "
                        f"not {type(value).__name__}.") from exc


# ------------------
# Engraving defaults
# ------------------

def normalizeEngravingDefaults(value: EngravingDefaults) -> EngravingDefaults:
    """Normalize EngravingDefaults object.

    :param value: The value to normalize.
    :raises TypeError: if ``value`` is not the accepted type.

    """
    from smufolib.objects.engravingDefaults import EngravingDefaults
    return normalizeInternalObjectType(
        value, EngravingDefaults, "EngravingDefaults object")


def normalizeEngravingDefaultsAttr(name: str,
                                   value: int | float
                                   | tuple[str, ...] | list[str] | None
                                   ) -> int | float | tuple[str, ...] | None:
    """Normalize engraving defaults attribute value based on name.

    :param name: The name of the attribute to normalize.
    :param value: The value to normalize.
    :raises TypeError: if ``name`` or ``value`` is not an accepted
     type.
    :raises ValueError: if ``name='textFontFamily'`` and ``value``
     contains an empty string.

    """
    if value is None:
        return None
    if name == 'textFontFamily':
        value = _normalizeStringList(name, value)
    elif not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be an int, float or None, "
                        f"not {type(value).__name__}.")
    return value


def _normalizeStringList(name: str,
                         value: tuple['str', ...] | list[str]
                         ) -> tuple['str']:
    # Normalize string list.
    if not isinstance(value, (tuple, list)):
        raise TypeError(f"{name} must be a list or None, "
                        f"not {type(value).__name__}.")
    for val in value:
        if not isinstance(val, str):
            raise TypeError(f"{name} items must be strings, "
                            f"not {type(value).__name__}.")
        if len(val) == 0:
            index = value.index(val)
            raise ValueError(f"{name} item at index {index} is empty.")
    return tuple(value)


# -------
# Request
# -------


def normalizeRequest(value: Request) -> Request:
    """Normalize Request object.

    :param value: The value to normalize.
    :raises TypeError: if ``value`` is not the accepted type.

    """
    from smufolib.request import Request
    return normalizeInternalObjectType(value, Request, "Request object")


def normalizeRequestPath(value: str | Path | None) -> str | None:
    """Normalize Request path.

    Relative paths are resolved automatically.

    :param value: The value to normalize.
    :raises TypeError: if ``value`` is not the accepted type.

    """
    if value is None:
        return None
    try:
        if isinstance(value, Path) or value.startswith('.'):
            return str(Path(value).resolve())
        return value
    except TypeError as exc:
        raise TypeError("Expected str or Path, not "
                        f"'{value.__class__.__name__}'.") from exc
