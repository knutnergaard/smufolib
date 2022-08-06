"""Test converters module for SMufoLib."""

import pytest
from smufolib import converters

# pylint: disable=missing-function-docstring, invalid-name

def testToDecimal():
    for value in ('U+0B00', 'uE0F0', 'uniE00C'):
        assert isinstance(converters.toDecimal(value), int)

    for value in ('U+0B0', 'uE0G0', 'unE00C'):
        with pytest.raises(ValueError):
            converters.toDecimal(value)


def testToUniHex():
    for value in (57344, '57344'):
        assert converters.toUniHex(value) == 'U+E000'

    with pytest.raises(ValueError):
        converters.toUniHex('23a45')


def testToUniName():
    for value in (57344, '57344', 'U+E000'):
        assert converters.toUniName(value, short=False) == 'uniE000'
        assert converters.toUniName(value, short=True) == 'uE000'

    with pytest.raises(ValueError):
        for value in ('U+ E000', 'U+E0G0'):
            converters.toUniName(value)
