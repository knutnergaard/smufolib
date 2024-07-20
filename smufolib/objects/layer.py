# pylint: disable=C0114
from fontParts.fontshell.layer import RLayer
from smufolib.objects.glyph import Glyph


class Layer(RLayer):
    """Environment implementation of :class:`fontParts.base.BaseLayer`."""

    # pylint: disable=too-few-public-methods

    glyphClass = Glyph
