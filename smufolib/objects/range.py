# pylint: disable=C0114
from __future__ import annotations
from typing import TYPE_CHECKING

from smufolib.request import Request
from smufolib import config
from smufolib.utils import normalizers

if TYPE_CHECKING:  # pragma: no cover
    from smufolib.objects.smufl import Smufl
    from smufolib.objects.glyph import Glyph
    from smufolib.objects.font import Font
    from smufolib.objects.layer import Layer

CONFIG = config.load()
METADATA = Request.ranges()


class Range:
    """SMuFL range-related metadata.

    This object provides access to metadata describing how a :class:`.Glyph` relates to
    SMuFL-defined glyph ranges. It is currently read-only and retrieves its data from
    :confval:`metadata.paths.ranges` or :confval:`metadata.fallbacks.ranges`.

    :param smufl: The range's parent :class:`.Smufl` object.

    This object is typically accessed through a glyph's Smufl metadata interface:

        >>> glyph = font["uniE050"]
        >>> range = glyph.smufl.ranges[0]

    You may also instantiate it independently and assign it to a glyph later:

        >>> range = Range()  # doctest: +SKIP

    """

    # pylint: disable=invalid-name

    def __init__(self, smufl: Smufl | None = None) -> None:
        self._smufl = smufl

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} '{self.name}' "
            f"('{self.start}-{self.end}') at {id(self)}>"
        )

    # -------
    # Parents
    # -------

    @property
    def smufl(self) -> Smufl | None:
        """Parent :class:`.Smufl` object.

        Example:

            >>> range.smufl  # doctest: +ELLIPSIS
            <Smufl in glyph 'uniE050' ['gClef'] ('public.default') at ...>


        """
        return self._smufl

    @smufl.setter
    def smufl(self, value: Smufl | None) -> None:
        if value is not None:
            self._smufl = normalizers.normalizeSmufl(value)

    @property
    def glyph(self) -> Glyph | None:
        """Parent :class:`.Glyph` object.

        Example:

            >>> range.glyph  # doctest: +ELLIPSIS
            <Glyph 'uniE050' ['gClef'] ('public.default') at ...>

        """
        if self._smufl is None:
            return None
        return self._smufl.glyph

    @property
    def font(self) -> Font | None:
        """Parent :class:`.Font` object.

        Example:

            >>> range.font  # doctest: +ELLIPSIS
            <Font 'MyFont Regular' path='/path/to/MyFont.ufo' at ...>

        """
        if self._smufl is None:
            return None
        return self._smufl.font

    @property
    def layer(self) -> Layer | None:
        """Parent :class:`.Layer` object.

        Example:

            >>> range.layer  # doctest: +ELLIPSIS
            <Layer 'public.default' at ...>

        """
        if self._smufl is None:
            return None
        return self._smufl.layer

    # ----
    # Data
    # ----

    @property
    def name(self) -> str | None:
        """Name of affiliated SMuFL range.

        Example:

            >>> range.name
            'clefs'

        """
        result = self._getAttribute("range_name")
        if isinstance(result, str):
            return result
        return None

    @property
    def description(self) -> str | None:
        """Description of affiliated SMuFL range.

        Example:

            >>> range.description
            'Clefs'

        """
        result = self._getAttribute("description")
        if isinstance(result, str):
            return result
        return None

    @property
    def glyphs(self) -> tuple[Glyph, ...]:
        """:class:`~smufolib.objects.glyph.Glyph` objects of Affiliated SMuFL range.

        Example:

            >>> range.glyphs  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
            (<Glyph 'uniE050' ['gClef'] ('public.default') at ...>,
            ...
            <Glyph 'uniE07F' ['clefChangeCombining'] ('public.default') at ...>)

        """
        result = self._getAttribute("glyphs")
        if isinstance(result, tuple):
            return result
        return ()

    @property
    def start(self) -> str | None:
        """Start unicode of affiliated SMuFL range.

        Example:

            >>> range.start
            'U+E050'

        """
        result = self._getAttribute("range_start")
        if isinstance(result, str):
            return result
        return None

    @property
    def end(self) -> str | None:
        """End unicode of affiliated SMuFL range.

        Example:

            >>> range.end
            'U+E07F'

        """
        result = self._getAttribute("range_end")
        if isinstance(result, str):
            return result
        return None

    def _getAttribute(self, name: str) -> str | tuple[Glyph, ...] | None:
        # Get metadata attributes from ranges.json.
        if self.glyph is None or METADATA is None or isinstance(METADATA, str):
            return None
        for range_, attributes in METADATA.items():
            if self._smufl is None or self._smufl.name not in attributes["glyphs"]:
                continue
            if name == "range_name":
                return range_
            if name == "glyphs":
                glyphs = tuple(
                    g
                    for n in attributes[name]
                    if (g := self._smufl.findGlyph(n)) is not None
                )
                return glyphs
            return attributes.get(name)
        return None
