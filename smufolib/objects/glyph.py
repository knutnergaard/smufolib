# pylint: disable=C0114
from __future__ import annotations

from fontParts.fontshell.glyph import RGlyph
from smufolib.objects.smufl import NAMES_LIB_KEY, Smufl
from smufolib.objects import _lib


class Glyph(RGlyph):
    """SMufoLib environment implementation of :class:`fontParts.base.BaseGlyph`.

    .. versionchanged:: 0.6.0

       The ``__repr__`` now includes the canonoical SMuFL glyph name (if present) in
       square brackets.

    This object is typically accessed through a :class:`.Font` object's inherent glyph
    dictionary. To instantiate the SMuFL glyph named U+E050 (*gClef*):

        >>> glyph = font["uniE050"]

    A glyph may also be instantiated independently and assigned to a font or glyph
    later:

        >>> glyph = Glyph()  # doctest: +SKIP

    """

    def _reprContents(self) -> list[str]:
        # Adds bracketed smufl name if available
        contents = [f"'{self.name}'"]
        smuflName = getattr(self.smufl, "name", None)
        if smuflName:
            contents.append(f"['{smuflName}']")
        if self.layer is not None:
            contents.append(f"('{self.layer.name}')")
        return contents

    def _set_name(self, value: str) -> None:
        # Set the name of the glyph and update :attr:`.Font.lib` if necessary.
        if self.font is not None:
            namesDict = _lib.getLibSubdict(self.font, NAMES_LIB_KEY)
            smuflName = self.smufl.name
            if namesDict and smuflName and self.naked().name in namesDict.values():
                namesDict[smuflName] = value
        self.naked().name = value

    @property
    def smufl(self) -> Smufl:
        """Glyph-specific instance of :class:`~smufolib.objects.smufl.Smufl`."""
        return Smufl(glyph=self)
