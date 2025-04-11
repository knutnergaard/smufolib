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
METADATA = Request(
    CONFIG["metadata.paths"]["ranges"], CONFIG["metadata.fallbacks"]["ranges"]
).json()


class Range:
    """SMuFL range-related metadata.

    Information about how a :class:`~smufolib.objects.glyph.Glyph`
    relates to SMuFL's own glyph ranges is accessible through this
    object. It is currently read-only, and retrieves it's data from the
    `ranges.json
    <https://w3c.github.io/smufl/latest/specification/ranges.html>`_
    metadata file.

    :param smufl: Parent :class:`~smufolib.objects.smufl.Smufl`.

    While this object is normally created as part of
    a :class:`~smufolib.objects.font.Font`, an
    orphan :class:`Range` object may be created like
    this::

        >>> range = Range()

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
        """Parent :class:`~smufolib.objects.smufl.Smufl` object."""
        return self._smufl

    @smufl.setter
    def smufl(self, value: Smufl | None) -> None:
        if value is not None:
            self._smufl = normalizers.normalizeSmufl(value)

    @property
    def glyph(self) -> Glyph | None:
        """Parent :class:`~smufolib.objects.glyph.Glyph` object."""
        if self._smufl is None:
            return None
        return self._smufl.glyph

    @property
    def font(self) -> Font | None:
        """Parent :class:`~smufolib.objects.font.Font` object."""
        if self._smufl is None:
            return None
        return self._smufl.font

    @property
    def layer(self) -> Layer | None:
        """Parent :class:`~smufolib.objects.layer.Layer` object."""
        if self._smufl is None:
            return None
        return self._smufl.layer

    # ----
    # Data
    # ----

    @property
    def name(self) -> str | None:
        """Name of affiliated SMuFL range.

        Example::

            >>> range.name
            timeSignatures

        """
        result = self._getAttribute("range_name")
        if isinstance(result, str):
            return result
        return None

    @property
    def description(self) -> str | None:
        """Description of affiliated SMuFL range.

        Example::

            >>> range.description
            Time signatures

        """
        result = self._getAttribute("description")
        if isinstance(result, str):
            return result
        return None

    @property
    def glyphs(self) -> tuple[Glyph, ...]:
        """:class:`~smufolib.objects.glyph.Glyph` objects of Affiliated SMuFL range.

        Example::

            >>> range.glyphs
            (<Glyph 'uniE080' ('public.default') at 4596284000>,
            ...
            <Glyph 'uniE09F' ('public.default') at 4632755792>)

        """
        result = self._getAttribute("glyphs")
        if isinstance(result, tuple):
            return result
        return ()

    @property
    def start(self) -> str | None:
        """Start unicode of affiliated SMuFL range.

        Example::

            >>> range.start
            U+E080

        """
        result = self._getAttribute("range_start")
        if isinstance(result, str):
            return result
        return None

    @property
    def end(self) -> str | None:
        """End unicode of affiliated SMuFL range.

        Example::

            >>> range.end
            U+E09F

        """
        result = self._getAttribute("range_end")
        if isinstance(result, str):
            return result
        return None

    def _getAttribute(self, name: str) -> str | tuple[Glyph, ...] | None:
        # Get metadata attributes from ranges.json.
        if self.glyph is None or METADATA is None:
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
