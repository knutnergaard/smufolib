"""Converters for SMufoLib."""
from __future__ import annotations
import re

# pylint: disable=invalid-name


def toDecimal(value: str) -> int:
    """Convert formatted unicode or uni name to decimal codepoint."""
    if _matchUnicode(value):
        try:
            decimal = int(value[-4:], 16)
        except ValueError:
            pass
    else:
        raise ValueError("Value is not a valid unicode.")

    return decimal


def toUniHex(value: int | str) -> str:
    """Convert decimal codepoint to formatted unicode hex."""
    return f'U+{hex(int(value)).upper()[2:]}'


def toUniName(value: str | int, short: bool = False) -> str:
    """Convert formatted unicode hex or decimal to 'uni' name.

    :param short: short form name with single 'u' prefix.
    """
    if isinstance(value, int) or value.isnumeric():
        numeral = hex(int(value)).upper()[2:]
    elif _matchUnicode(value):
        numeral = hex(int(value[-4:], 16)).upper()[2:]
    else:
        raise ValueError("Value must be formatted unicode string or decimal.")

    if short:
        return f'u{numeral}'
    return f'uni{numeral}'


def _matchUnicode(value):
    # Match value to unicode regex
    return re.fullmatch(r'(u\+?|uni)([a-f]|[0-9]){4}', value.lower())
