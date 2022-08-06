"""Validator module for SMufoLib."""
from typing import Any

# pylint: disable=invalid-name


def isFloat(string: Any) -> bool:
    """Check if string is float."""
    if '.' not in string:
        return False
    try:
        float(string)
        return True
    except ValueError:
        return False


def validateGlyph(glyph: object, inform: bool = True) -> bool:
    """Valitator for iterations through font glyphs.

    Function invalidates unencoded, empty or unannoted glyphs and prints
    information to console if inform is True.
    """
    if not glyph:
        return False

    if not glyph.codepoint:
        if inform:
            print(f"Skipping unencoded glyph: {glyph.name}")
        return False

    if not glyph.rGlyph.note:
        if inform:
            print(f"Skipping unannotated glyph: {glyph.name}")
        return False
    return True
