# pylint: disable=C0114
from __future__ import annotations
from typing import TYPE_CHECKING

from fontParts.fontshell.glyph import RGlyph
from smufolib.objects.smufl import Smufl

if TYPE_CHECKING:
    from fontParts.fontshell.anchor import RAnchor
    from fontParts.fontshell.contour import RContour
    from fontParts.fontshell.component import RComponent
    from fontParts.fontshell.guideline import RGuideline


class Glyph(RGlyph):
    """SMufoLib environment implementation of :class:`fontParts.base.BaseGlyph`.

    Glyphs are usually accessed through a :class:`~smufolib.objects.font.Font` objects
    inherent glyph dictionary. To instantiate the SMuFL glyph named `'uniE030'`
    (**single barline**)::

        >>> glyph = font['uniE030']

    """

    def _set_name(self, value: str) -> None:
        # Set the name of the glyph and update :attr:`.Font.lib` if necessary.
        if self.font is not None:
            namesDict = self.font.lib.get("com.smufolib.names", {})
            smuflName = self.smufl.name
            if smuflName and self.naked().name in namesDict.values():
                namesDict[smuflName] = value
        self.naked().name = value

    @property
    def smufl(self) -> Smufl:
        """Glyph-specific instance of :class:`~smufolib.objects.smufl.Smufl`."""
        return Smufl(glyph=self)

    @property
    def width(self) -> int | float:
        """Proxy of :attr:`fontParts.base.BaseGlyph.width`."""
        # pylint: disable=C2801
        return RGlyph.width.__get__(self, type(self))

    @width.setter
    def width(self, value: int | float) -> None:
        # pylint: disable=C2801
        RGlyph.width.__set__(self, value)

    @property
    def height(self) -> int | float:
        """Proxy of :attr:`fontParts.base.BaseGlyph.height`."""
        # pylint: disable=C2801
        return RGlyph.height.__get__(self, type(self))

    @height.setter
    def height(self, value: int | float) -> None:
        # pylint: disable=C2801
        RGlyph.height.__set__(self, value)

    @property
    def anchors(self) -> tuple[RAnchor, ...]:
        """Proxy of :attr:`fontParts.base.BaseGlyph.anchors`."""
        return super().anchors

    @property
    def contours(self) -> tuple[RContour, ...]:
        """Proxy of :attr:`fontParts.base.BaseGlyph.contours`."""
        return super().contours

    @property
    def components(self) -> tuple[RComponent, ...]:
        """Proxy of :attr:`fontParts.base.BaseGlyph.components`."""
        return super().components

    @property
    def guidelines(self) -> tuple[RGuideline, ...]:
        """Proxy of :attr:`fontParts.base.BaseGlyph.guidelines`."""
        return super().guidelines
