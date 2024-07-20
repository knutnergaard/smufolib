# pylint: disable=C0114
from fontParts.fontshell.font import RFont
from smufolib.objects.layer import Layer
from smufolib.objects.smufl import Smufl


class Font(RFont):
    """Environment implementation of :class:`fontParts.base.BaseFont`.

    To import the :class:`Font` object and instantiate a font::

        >>> from smufolib import Font
        >>> font = Font('path/to/my/font.ufo')

    """

    # pylint: disable=too-few-public-methods

    layerClass = Layer

    @property
    def smufl(self) -> Smufl:
        """Font instance of :class:`~smufolib.objects.smufl.Smufl`."""
        return Smufl(font=self)
