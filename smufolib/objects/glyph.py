# pylint: disable=C0114
from __future__ import annotations

from fontParts.fontshell.glyph import RGlyph
from smufolib.objects.smufl import Smufl


class Glyph(RGlyph):
    """SMufoLib environment implementation of :class:`fontParts.base.BaseGlyph`.

    .. versionchanged:: 0.6.0

       The ``__repr__`` now includes the canonoical SMuFL glyph name (if present) in
       square brackets.

    Glyphs are usually accessed through a :class:`~smufolib.objects.font.Font` objects
    inherent glyph dictionary. To instantiate the SMuFL glyph named U+E030 (*single
    barline*)::

        >>> glyph = font["uniE030"]

    """

    def _reprContents(self) -> list[str]:
        # Adds bracketed smufl name if available
        contents = [f"'{self.name}'"]
        smuflName = getattr(self.smufl, "name", None)
        if smuflName:
            contents.append(f"['{smuflName}']")
        if self.layer is not None:
            contents.append(f"('{self.layer.name})'")
        return contents

    def _set_name(self, value: str) -> None:
        # Set the name of the glyph and update :attr:`.Font.lib` if necessary.
        if self.font is not None:
            namesDict = self.smufl.names
            smuflName = self.smufl.name
            if namesDict and smuflName and self.naked().name in namesDict.values():
                namesDict[smuflName] = value
        self.naked().name = value

    @property
    def smufl(self) -> Smufl:
        """Glyph-specific instance of :class:`~smufolib.objects.smufl.Smufl`."""
        return Smufl(glyph=self)
