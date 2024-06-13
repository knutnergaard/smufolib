# pylint: disable=C0114
from fontParts.fontshell.glyph import RGlyph

from smufolib.objects.smufl import Smufl


class Glyph(RGlyph):
    """Environment implementation of :class:`fontParts.base.BaseGlyph`.

    Glyphs are usually accessed through
    a :class:`~smufolib.objects.font.Font` objects inherent glyph
    dictionary. To instantiate the SMuFL glyph named ``uniE030``
    (single barline)::

        >>> glyph = font['uniE030']

    """

    # pylint: disable=too-few-public-methods

    @property
    def smufl(self) -> Smufl:
        """Glyph instance of :class:`~smufolib.objects.smufl.Smufl`."""
        return Smufl(glyph=self)
