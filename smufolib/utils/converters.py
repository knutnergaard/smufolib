"""Utility functions for converting values between various formats.

These functions focus on converting between different string and numeric formats
related to measurements, Unicode codepoints, and letter casing.

To import the module:

    >>> from smufolib import converters

"""

from __future__ import annotations
import re

from smufolib.utils import error, stdUtils


# pylint: disable=C0103
def convertMeasurement(
    measurement: int | float | str,
    targetUnit: str,
    unitsPerEm: int | float,
    rounded: bool = False,
) -> int | float:
    """Convert between units of measurement based on UPM size.

    :param measurement: The value to convert.
    :param targetUnit: Unit to convert to.
    :param unitsPerEm: The UPM value to base conversion on.
    :param rounded: Whether to round result to nearest integer.
    :raises TypeError: If `measurement` is not an accepted type.
    :raises ValueError: If `targetUnit` is neither ``"spaces"``
     nor ``"units"``.

    Example:

        >>> converters.convertMeasurement(0.795, "units", 1000, rounded=False)
        198.75
        >>> converters.convertMeasurement(0.795, "units", 1000, rounded=True)
        199
        >>> converters.convertMeasurement("198.75", "spaces", 1000, rounded=True)
        0.795

    """
    error.validateType(measurement, (int, float, str), "measurement")
    error.suggestValue(targetUnit, ("spaces", "units"), "targetUnit")

    space = unitsPerEm / 4
    measurement = float(measurement)
    if targetUnit == "spaces":
        measurement /= space
        return round(measurement, 3)

    measurement *= space
    return round(measurement) if rounded else measurement


def toDecimal(string: str) -> int:
    """Convert formatted unicode or uni name to decimal codepoint.

    Function accepts any hexadecimal string within the Unicode range
    (U+0000 -- U+10FFFF) prefixed by ``"u"``, ``"U+"`` or ``"uni"``.

    :param string: The value to convert.
    :raises TypeError: If `string` is not the accepted type.
    :raises ValueError: If `string` is not a valid formatted
        unicode codepoint or outside the unicode range
        (U+0000 -- U+10FFFF).

    Example:

        >>> converters.toDecimal("uniE000")
        57344
        >>> converters.toDecimal("u1D100")
        119040
        >>> converters.toDecimal("U+0A00")
        2560

    """
    error.validateType(string, str, "string")
    unicodeHex = _findUnicodeHex(string)
    if not unicodeHex:
        raise ValueError(
            error.generateErrorMessage("invalidFormat", objectName="string")
        )
    decimal = int(unicodeHex, 16)

    if stdUtils.isInUnicodeRange(decimal):
        return decimal

    raise ValueError(
        error.generateErrorMessage(
            "unicodeOutOfRange", objectName="string", start="U+0000", end="U+10FFFF"
        )
    )


def toUniHex(value: int | str) -> str:
    """Convert decimal codepoint or uni-name to formatted Unicode hex.

    :param value: The decimal value to convert.
    :raises TypeError: If `value` is not the accepted type.
    :raises ValueError: If `value` is outside the Unicode range
        (U+0000 -- U+10FFFF).

    Example:

        >>> converters.toUniHex(2560)
        'U+0A00'
        >>> converters.toUniHex("uni0A00")
        'U+0A00'

    """
    error.validateType(value, (int, str), "codepoint")
    if isinstance(value, str):
        unicodeHex = _findUnicodeHex(value)
        if not unicodeHex:
            raise ValueError(
                error.generateErrorMessage("invalidFormat", objectName="value")
            )
        value = int(unicodeHex, 16)

    if stdUtils.isInUnicodeRange(value):
        return f"U+{value:04X}"

    raise ValueError(
        error.generateErrorMessage(
            "unicodeOutOfRange", objectName="value", start="U+0000", end="U+10FFFF"
        )
    )


def toUniName(value: int | str, short: bool = False) -> str:
    """Convert decimal codepoint or Unicode notation string to uni-name.

    Function accepts any integer or prefixed hexadecimal string (e.g., ``"U+E000"``,
    ``"uE000"``, ``"uniE000"``) within the Unicode range (U+0000 -- U+10FFFF).

    :param value: The value to convert.
    :param short: Whether to return name with single ``"u"`` prefix.
    :raises TypeError: If `value` is not an accepted type.
    :raises ValueError: If `value` is outside the Unicode range (U+0000 -- U+10FFFF) or
        not a valid formatted string.

    Example:

        >>> converters.toUniName("U+E000")
        'uniE000'
        >>> converters.toUniName('U+E000', short=True)
        'uE000'
        >>> converters.toUniName(57344)
        'uniE000'

    """
    error.validateType(value, (int | str), "value")

    if isinstance(value, str):
        unicodeHex = _findUnicodeHex(value)
        if unicodeHex is None:
            raise ValueError(
                error.generateErrorMessage("invalidFormat", objectName="value")
            )
        value = int(unicodeHex, 16)

    if stdUtils.isInUnicodeRange(value):
        prefix = "u" if short else "uni"
        return f"{prefix}{value:04X}"

    raise ValueError(
        error.generateErrorMessage(
            "unicodeOutOfRange", objectName="value", start="U+0000", end="U+10FFFF"
        )
    )


def toKebab(camelCaseString: str) -> str:
    """Convert camelCase to kebab-case.

    :param camelCaseString: The string to convert.

    Example:

        >>> converters.toKebab("camelCase")
        'camel-case'

    """
    return re.sub(r"(?<!^)(?=[A-Z]{1})", "-", camelCaseString).lower()


def toNumber(numericString: str) -> int | float:
    """Convert numeric string to number.

    :param numericString: The value to convert.
    :raises ValueError: If `numericString` is not a valid int or float.

    Example:

        >>> converters.toNumber("57344")
        57344
        >>> converters.toNumber("57.344")
        57.344
        >>> converters.toNumber("E000")
        57344

    """
    error.validateType(numericString, str, "numericString")
    try:
        if stdUtils.isFloat(numericString):
            return float(numericString)
        if numericString.isnumeric():
            return int(numericString)
        return int(numericString, 16)
    except ValueError as exc:
        raise ValueError(
            error.generateErrorMessage("numericValue", objectName="numericString")
        ) from exc


def toIntIfWhole(number: int | float) -> int | float:
    """Convert float without a fractional part to integer.

    If `number` is already an :class:`int` or the :class:`float` has a
    fractional part, it is left unchanged.

    :param number: The value to convert.

    Example:

        >>> converters.toIntIfWhole(34.0)
        34
        >>> converters.toIntIfWhole(34.1)
        34.1

    """
    if isinstance(number, float) and number.is_integer():
        return int(number)
    return number


def _findUnicodeHex(string: str) -> str | None:
    # Find the hex in various unicode value configurations.
    # If found, add prefix and return value or None.
    error.validateType(string, str, "string")
    pattern = r"(?:^u\+?|^uni)([0-9a-f]{4,})"
    result = re.search(pattern, string, flags=re.IGNORECASE)
    if not result:
        return None
    return result.group(1)
