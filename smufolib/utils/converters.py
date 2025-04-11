"""Utility functions for converting values between various formats.

These functions focus on conversion different string and number formats
related to measurements, Unicode codepoints and letter case.

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
    :raises ValueError: If `targetUnit` is neither ``'spaces'``
     nor ``'units'``.

    Example::

        >>> convertMeasurement(0.795, 'units', 1000, rounded=False)
        198.75
        >>> convertMeasurement(0.795, 'units', 1000, rounded=True)
        199
        >>> convertMeasurement('198.75', 'spaces', 1000, rounded=True)
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


def toDecimal(unicodeString: str) -> int:
    """Convert formatted unicode or uni name to decimal codepoint.

    Function accepts any hexadecimal string within the Unicode range
    (U+0000 – U+10FFFF) prefixed by ``'u'``, ``'U+'`` or ``'uni'``.

    :param unicodeString: The value to convert.
    :raises TypeError: If `unicodeString` is not the accepted type.
    :raises ValueError: If `unicodeString` is not a valid formatted
        unicode codepoint or outside the unicode range
        (U+0000 – U+10FFFF).

    Example::

        >>> toDecimal('uniE000')
        57344
        >>> toDecimal('u1D100')
        119040
        >>> toDecimal('U+0A00')
        2560

    """
    error.validateType(unicodeString, str, "unicodeString")
    unicodeHex = _findUnicodeHex(unicodeString)
    if not unicodeHex:
        raise ValueError(
            error.generateErrorMessage("invalidFormat", objectName="unicodeString")
        )

    decimal = int(toNumber(unicodeHex))  # Casting to int to please mypy.
    if _isInUnicodeRange(decimal):
        return decimal

    raise ValueError(
        error.generateErrorMessage("unicodeOutOfRange", objectName="unicodeString")
    )


def toUniHex(codepoint: int) -> str:
    """Convert decimal codepoint to formatted Unicode hex.

    :param codepoint: The decimal value to convert.
    :raises TypeError: If `codepoint` is not the accepted type.
    :raises ValueError: If `codepoint` is outside the Unicode range
        (U+0000 – U+10FFFF).

    Example::

        >>> toUniHex(2560)
        'U+0A00'

    """
    error.validateType(codepoint, int, "codepoint")

    if _isInUnicodeRange(codepoint):
        return f"U+{str(hex(codepoint).upper()[2:]).zfill(4)}"
    raise ValueError(
        error.generateErrorMessage("unicodeOutOfRange", objectName="codepoint")
    )


def toUniName(value: str | int, short: bool = False) -> str:
    """Convert formatted Unicode hex or decimal to 'uni' name.

    Function accepts any integer or prefixed hexadecimal string
    within the Unicode range (U+0000 – U+10FFFF).

    :param value: The value to convert.
    :param short: Whether to return name with single ``'u'`` prefix.
    :raises TypeError: If `value` is not an accepted type.
    :raises ValueError: If `value` is outside the Unicode range
        (U+0000 – U+10FFFF) or not a valid formatted string.

    Example::

        >>> toUniName('U+E000')
        'uniE000'
        >>> toUniName('U+E000', short=True)
        'uE000'
        >>> toUniName(57344)
        'uniE000'

    """
    prefix = "u" if short else "uni"

    error.validateType(value, (str, int), "value")
    if isinstance(value, str):
        unicodeHex = _findUnicodeHex(value)
        if unicodeHex is None:
            raise ValueError(
                error.generateErrorMessage("invalidFormat", objectName="value")
            )
    else:
        unicodeHex = "0x" + format(value, "X").zfill(4)

    if not _isInUnicodeRange(int(unicodeHex, 16)):
        raise ValueError(
            error.generateErrorMessage("unicodeOutOfRange", objectName="value")
        )

    return prefix + unicodeHex[2:].upper()


def toKebab(camelCaseString: str) -> str:
    """Convert camelCase to kebab-case.

    :param camelCaseString: The string to convert.

    Example::

        >>> toKebab('camelCase')
        'camel-case'

    """
    return re.sub(r"(?<!^)(?=[A-Z]{1})", "-", camelCaseString).lower()


def toNumber(numericString: str) -> int | float:
    """Convert numeric string to number.

    :param numericString: The value to convert.
    :raises ValueError: If `numericString` is not a valid int or float.

    Example::

        >>> toNumber('57344')
        57344
        >>> toNumber('57.344')
        57.344
        >>> toNumber('E000')
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

    Example::

        >>> toIntIfWhole(34.0)
        34
        >>> toIntIfWhole(34.1)
        34.1

    """

    if isinstance(number, float) and number.is_integer():
        return int(number)
    return number


def _findUnicodeHex(unicodeString: str) -> str | None:
    # Find the hex in various unicode value configurations.
    # If found, add prefix and return value or None.
    error.validateType(unicodeString, str, "unicodeString")
    pattern = r"((?<=^u)|(?<=^u\+)|(?<=^uni))([a-f]|[0-9]){4,}"
    result = re.search(pattern, unicodeString, flags=re.IGNORECASE)
    if not result:
        return None
    return f"0x{result.group(0)}"


def _isInUnicodeRange(codepoint: int) -> bool:
    # Check if number is within Unicode range
    if 0x0 <= codepoint <= 0x10FFFF:
        return True
    return False
