"""
Converter module for SMufoLib.
"""
import re

# pylint: disable=invalid-name


def toCamelCase(string: str) -> str:
    """
    Simple camelCase converter.
    Handles most common word separators.
    """
    words = re.split(r'\s|_|-|\.', string)
    return words[0].lower() + ''.join([w.title() for w in words[1:]])


def toDecimal(value: str) -> int:
    """
    Converts formatted unicode or uni name to decimal codepoint.
    """
    if not (len(value) == 6 and value.startswith('U+')
            or len(value) == 7 and value.startswith('uni')):
        raise ValueError("Value is not a valid unicode.")
    return int(value[3:], 16)


def toUniHex(value: int) -> str:
    """
    Converts decimal codepoint to formatted unicode hex.
    """
    return f'U+{hex(value).upper()[2:]}'


def toUniName(value: str) -> str:
    """
    Converts formatted unicode hex or decimal to 'uni' name.
    """
    if isinstance(value, int) or value.isnumeric():
        return f'uni{hex(int(value)).upper()[2:]}'
    if value.startswith('U+'):
        return 'uni' + value[2:]
    raise ValueError("Value must be formatted unicode string or decimal.")
