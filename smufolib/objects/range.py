
"""Range metadata module for SMufoLib."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Tuple
from pathlib import Path

from smufolib.request import Request
from smufolib import config

if TYPE_CHECKING:
    from smufolib.objects.smufl import Smufl
    from smufolib.objects.glyph import Glyph
    from smufolib.objects.font import Font
    from smufolib.objects.layer import Layer

CONFIG = config.load()
METADATA = Request(CONFIG['metadata.paths']['ranges'],
                   CONFIG['metadata.fallbacks']['ranges']).json()


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
        return (f"<{self.__class__.__name__} '{self.name}' "
                f"('{self.start}–{self.end}') at {id(self)}>")

    # -------
    # Parents
    # -------

    @property
    def smufl(self) -> Smufl | None:
        """Parent :class:`~smufolib.objects.smufl.Smufl` object."""
        return self._smufl

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
        return self._getAttribute('range_name')

    @property
    def description(self) -> str | None:
        """Description of affiliated SMuFL range.

        Example::

            >>> range.description
            Time signatures

        """
        return self._getAttribute('description')

    @property
    def glyphs(self) -> Tuple[Glyph, ...] | None:
        """:class:`~smufolib.objects.glyph.Glyph` objects of Affiliated SMuFL range.

        Example::

            >>> range.glyphs
            (<Glyph 'uniE080' ('public.default') at 4596284000>,
            ...
            <Glyph 'uniE09F' ('public.default') at 4632755792>)

        """
        return self._getAttribute('glyphs')

    @property
    def start(self) -> int | None:
        """Start unicode of affiliated SMuFL range.

        Example::

            >>> range.start
            U+E080

        """
        return self._getAttribute('range_start')

    @property
    def end(self) -> int | None:
        """End unicode of affiliated SMuFL range.

        Example::

            >>> range.end
            U+E09F

        """
        return self._getAttribute('range_end')

    def _getAttribute(self, name: str) -> str | List[str] | None:
        # Get metadata attributes from ranges.json.
        if self.glyph is None or METADATA is None:
            return None
        for range_, attributes in METADATA.items():
            if self.smufl.name not in attributes['glyphs']:
                continue
            if name == 'range_name':
                return range_
            if name == 'glyphs':
                return tuple(self.smufl.findGlyph(n) for n in attributes[name])
            return attributes[name]
