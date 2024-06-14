from __future__ import annotations
from typing import TYPE_CHECKING, Any
from pathlib import Path
import re
from typeguard import typechecked

from smufolib import stdUtils

# pylint: disable=invalid-name


def convertMeasurement(value: int | float | str,
                       convertTo: str,
                       unitsPerEm: int | float,
                       rounded: bool = False) -> int | float | None:
    """Convert between units of measurement based on UPM size.

    :param value: The value to convert.
    :param convertTo: Unit to convert to.
    :param unitsPerEm: The UPM value to base conversion on.
    :param rounded: Whether to round result to nearest integer.
    :raises TypeError: if ``value`` is not an accepted type.
    :raises ValueError: unless ``convertTo='spaces'`` or ``='units'``.

    """
    try:
        space = unitsPerEm / 4
        value = float(value)
        if convertTo == 'spaces':
            value /= space
            return round(value, 3)

        if convertTo == 'units':
            value *= space
            return round(value) if rounded else value

        raise ValueError(
            f"Conversion must be 'spaces' or 'units', not '{convertTo}'.")
    except TypeError as exc:
        raise TypeError("Value must be int, float or numeric string, "
                        f"not {type(value).__name__}.") from exc


def toDecimal(value: str) -> int:
    """Convert formatted unicode or uni name to decimal codepoint.

    Function accepts any hexadecimal string within the Unicode range
    (U+0000 – U+10FFFF) prefixed by ``'u'``, ``'U+'`` or ``'uni'``.

    :param value: The value to convert.
    :raises TypeError: if value is not the accepted type.
    :raises ValueError: if ``value`` is not a valid formatted unicode
     codepoint.

    """
    try:
        unicodeHex = _findUnicodeHex(value)
        if not unicodeHex:
            raise ValueError("Value is not a valid format.")

        decimal = toNumber(unicodeHex)
        if _isInUnicodeRange(decimal):
            return decimal

        raise ValueError(
            "Value is outside the Unicode range (U+0000 – U+10FFFF).")
    except TypeError as exc:
        raise TypeError(
            f"Value must be string, not {type(value).__name__}.") from exc


def toUniHex(value: int) -> str:
    """Convert decimal codepoint to formatted Unicode hex.

    :param value: The decimal to convert.
    :raises TypeError: if value is not the accepted type.
    :raises ValueError: if ``value`` is outside the Unicode range
     (U+0000 – U+10FFFF).

    """
    try:
        if _isInUnicodeRange(value):
            return f'U+{str(hex(value).upper()[2:]).zfill(4)}'
        raise ValueError(
            "Value is outside the Unicode range (U+0000 – U+10FFFF).")
    except TypeError as exc:
        raise TypeError(
            f"Value must be int, not {type(value).__name__}.") from exc


def toUniName(value: str | int, short: bool = False) -> str:
    """Convert formatted Unicode hex or decimal to 'uni' name.

    Function accepts any integer or prefixed hexadecimal string
    within the Unicode range(U+0000 – U+10FFFF).

    :param value: The value to convert.
    :param short: Whether to return name with single ``'u'`` prefix.
    :raises TypeError: if value is not an accepted type.
    :raises ValueError: if ``value`` is outside the Unicode range
     (U+0000 – U+10FFFF) or not a valid formatted string.

    """
    prefix = 'u' if short else 'uni'

    try:
        unicodeHex = _findUnicodeHex(value)
        if not unicodeHex:
            raise ValueError("String is not a valid format.")
        if _isInUnicodeRange(int(unicodeHex, 16)):
            return prefix + unicodeHex.upper()
    except TypeError:
        try:
            if _isInUnicodeRange(value):
                return prefix + str(hex(value).upper()[2:]).zfill(4)
        except TypeError as exc:
            raise TypeError(
                f"Value must be int or string, not {type(value).__name__}."
            ) from exc
    raise ValueError(
        "Value is outside the Unicode range (U+0000 – U+10FFFF).")


def toKebab(string):
    """Convert camelCase to kebab-case.

    :param string: The string to convert.

    """
    return re.sub(r'(?<!^)(?=[A-Z])', '-', string).lower()


def toNumber(string: str) -> int | float:
    """Convert numeric string to number.

    :param value: The value to convert.
    :raises ValueError: if ``string`` is not a valid int or float.

    """
    if stdUtils.isFloat(string):
        return float(string)
    if string.isnumeric():
        return int(string)
    try:
        return int(string, 16)
    except ValueError as exc:
        raise ValueError("Value must be a valid int or float.") from exc


def _findUnicodeHex(string: str) -> str | None:
    # Find the ending hex in various unicode value configurations.
    pattern = r'((?<=^u)|(?<=^u\+)|(?<=^uni))([a-f]|[0-9]){4,}'
    result = re.search(pattern, string, flags=re.IGNORECASE)
    if result:
        try:
            return result.group(0)
        except AttributeError:
            return None


def _isInUnicodeRange(number: int) -> bool:
    # check if number is within unicode range
    if 0x0 <= number <= 0x10FFFF:
        return True
    return False
