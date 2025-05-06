# pylint: disable=C0114
import defcon
from fontParts.base.font import BaseFont
from fontParts.fontshell.font import RFont
from smufolib.objects.layer import Layer
from smufolib.objects.smufl import Smufl
from smufolib.utils import error


class Font(RFont):
    """SMufoLib environment implementation of :class:`fontParts.base.BaseFont`.

    :param pathOrObject: The source used to initialize the font.

        - If :obj:`None`, a new, empty font will be created.
        - If a :class:`str`, it is interpreted as a path to an existing UFO file.
        - If an unwrapped native font object (e.g., a :class:`defcon.Font`) or a
          :class:`fontParts.base.BaseFont`, it will be wrapped.

        .. versionadded:: 0.6.0

            Support for initializing from an existing :class:`fontParts.base.BaseFont`
            instance.


    Example::

        >>> font = Font('path/to/font.ufo')     # Load from path
        >>> font = Font(BaseFont())             # Wrap an existing font

    """

    # pylint: disable=too-few-public-methods

    layerClass = Layer

    def __init__(self, pathOrObject: str | defcon.Font | BaseFont | None = None):
        if isinstance(pathOrObject, BaseFont):
            try:
                pathOrObject = pathOrObject.naked()
            except AttributeError:
                error.generateTypeError(
                    pathOrObject, (BaseFont, defcon.Font), "pathOrObject"
                )
        super().__init__(pathOrObject)

    @property
    def smufl(self) -> Smufl:
        """Font-specific instance of :class:`~smufolib.objects.smufl.Smufl`."""
        return Smufl(font=self)
