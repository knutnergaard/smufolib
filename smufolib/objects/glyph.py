# pylint: disable=C0114
from fontParts.fontshell.glyph import RGlyph
from smufolib.objects.smufl import Smufl


class Glyph(RGlyph):
    """Environment implementation of :class:`fontParts.base.BaseGlyph`.

    Glyphs are usually accessed through
    a :class:`~smufolib.objects.font.Font` objects inherent glyph
    dictionary. To instantiate the SMuFL glyph named `uniE030`
    (single barline)::

        >>> glyph = font['uniE030']

    """

    def _set_name(self, value):
        # Set the name of the glyph and update :attr:`.Font.lib` if necessary.
        if self.font is not None:
            namesDict = self.font.lib.get("com.smufolib.names", {})
            smuflName = self.smufl.name
            if smuflName and self.naked().name in namesDict.values():
                namesDict[smuflName] = value
        self.naked().name = value

    @property
    def smufl(self) -> Smufl:
        """Glyph instance of :class:`~smufolib.objects.smufl.Smufl`."""
        return Smufl(glyph=self)
