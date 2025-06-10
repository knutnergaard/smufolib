# pylint: disable=C0114
from fontParts.fontshell.layer import RLayer
from smufolib.objects.glyph import Glyph


class Layer(RLayer):
    """SMufoLib environment implementation of :class:`fontParts.base.BaseLayer`."""

    # pylint: disable=too-few-public-methods

    glyphClass = Glyph

    def _removeGlyph(self, name, **kwargs):
        layer = self.naked()
        # Clean up font.lib.
        self[name].smufl.name = None
        del layer[name]
