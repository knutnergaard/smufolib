# pylint: disable=C0114
import defcon
from fontParts.base.font import BaseFont
from fontParts.fontshell.font import RFont
from smufolib.objects.layer import Layer
from smufolib.objects.smufl import Smufl


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

    Examples:

        >>> from smufolib import Font
        >>> font = Font("path/to/MyFont.ufo")  # doctest: +SKIP

        >>> from fontParts.fontshell import RFont
        >>> font = Font(RFont())  # doctest: +SKIP

    """

    # pylint: disable=too-few-public-methods

    layerClass = Layer

    def __init__(self, pathOrObject: str | defcon.Font | BaseFont | None = None):
        if isinstance(pathOrObject, BaseFont):
            try:
                pathOrObject = pathOrObject.naked()
            except AttributeError as exc:
                raise TypeError(
                    "Expected 'pathOrObject' to be of type str, "
                    "defcon.Font or BaseFont with naked()."
                ) from exc

        super().__init__(pathOrObject)

    @property
    def smufl(self) -> Smufl:
        """Font-specific instance of :class:`~smufolib.objects.smufl.Smufl`."""
        return Smufl(font=self)
