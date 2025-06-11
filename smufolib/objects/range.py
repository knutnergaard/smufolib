# pylint: disable=C0114
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Type
from collections.abc import Iterator

from smufolib.request import Request
from smufolib import config
from smufolib.utils import converters, normalizers
from smufolib.objects import _lib

if TYPE_CHECKING:  # pragma: no cover
    from smufolib.objects.smufl import Smufl
    from smufolib.objects.glyph import Glyph
    from smufolib.objects.font import Font
    from smufolib.objects.layer import Layer

CONFIG = config.load()
EDITABLE = editable = CONFIG["ranges"]["editable"]
METADATA = Request.ranges()
RANGES_LIB_KEY = "com.smufolib.ranges"

RangeValue = str | int | tuple["Glyph", ...] | None
T = TypeVar("T", bound=RangeValue)


class Range:
    """SMuFL range-related metadata.

    This object provides access to metadata describing how a :class:`.Glyph` relates to
    SMuFL-defined glyph ranges. Specified range data is sourced from
    :confval:`metadata.paths.ranges`, falling back to
    :confval:`metadata.fallbacks.ranges` if the former is unavailable.

    Ranges are read-only by default. Editability is controlled globally via the
    :confval:`ranges.editable` configuration setting. New custom ranges may be added
    using :meth:`.Smufl.newRange`. This data will be stored in the font's :class:`Lib
    <fontParts.base.BaseLib>` object.

    .. versionadded:: 0.7.0

        Support for optional editability.

    :param smufl: The range's parent :class:`.Smufl` object.

    This object is typically accessed through a glyph's Smufl metadata interface:

        >>> glyph = font["uniE050"]
        >>> range = glyph.smufl.ranges[0]

    You may also instantiate it independently and assign it to a glyph later:

        >>> range = Range()  # doctest: +SKIP

    """

    # pylint: disable=invalid-name

    def __init__(self, smufl: Smufl | None = None, _internal: bool = True) -> None:
        self._smufl = smufl
        self._internal = _internal

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} {self.name!r} "
            f"({self.strStart}-{self.strEnd}) editable={EDITABLE} at {id(self)}>"
        )

    def __bool__(self) -> bool:
        return self.name is not None and self.start is not None and self.end is not None

    def __contains__(self, item: Glyph) -> bool:
        return item in self.glyphs if self.glyphs else False

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Range)
            and self.name == other.name
            and self.start == other.start
            and self.end == other.end
        )

    def __hash__(self) -> int:
        return hash((self.name, self.start, self.end))

    def __iter__(self) -> Iterator[Glyph]:
        return iter(self.glyphs or ())

    def __len__(self) -> int:
        return len(self.glyphs) if self.glyphs is not None else 0

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
        """Unique identifier of the glyph's affiliated SMuFL range.

        Example:

            >>> range.name
            'clefs'

        """
        return self._getAttribute("identifier", str)

    @property
    def description(self) -> str | None:
        """Human-readable description of the glyph's affiliated SMuFL range.

        Example:

            >>> range.description
            'Clefs'

        """
        return self._getAttribute("description", str)

    @property
    def glyphs(self) -> tuple[Glyph, ...] | None:
        """:class:`.Glyph` objects of the glyph's affiliated SMuFL range.

        Example:

            >>> range.glyphs  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
            (<Glyph 'uniE050' ['gClef'] ('public.default') at ...>,
            ...
            <Glyph 'uniE07F' ['clefChangeCombining'] ('public.default') at ...>)

        """
        return self._getAttribute("glyphs", tuple)

    @property
    def start(self) -> int | None:
        """Start unicode of the glyph's affiliated SMuFL range.

        Example:

            >>> range.start
            57424

        """
        return self._getAttribute("range_start", int)

    @property
    def end(self) -> int | None:
        """End unicode of the glyph's affiliated SMuFL range.

        Example:

            >>> range.end
            57471

        """
        return self._getAttribute("range_end", int)

    @property
    def strStart(self) -> str | None:
        """Start of the glyph's affiliated SMuFL range as Unicode string.

        Example:

            >>> range.strStart
            'U+E050'

        """
        return self._getAttribute("range_start", str)

    @property
    def strEnd(self) -> str | None:
        """End of the glyph's affiliated SMuFL range as Unicode string.

        Example:

            >>> range.strEnd
            'U+E07F'

        """
        return self._getAttribute("range_end", str)

    def _getAttribute(self, key: str, expectedType: Type[T]) -> T | None:
        # Get metadata attributes from ranges.json.
        data = (
            _lib.getLibSubdict(self.font, RANGES_LIB_KEY)
            if self._internal
            else METADATA
        )

        if self.glyph is None or data is None or isinstance(data, str):
            return None

        for range_, attributes in data.items():
            if self._smufl is None or (
                not self._internal and self._smufl.name not in attributes["glyphs"]
            ):
                continue
            value = attributes.get(key)
            if key == "identifier":
                value = range_
            if key == "glyphs":
                value = tuple(
                    g
                    for n in attributes[key]
                    if (g := self._smufl.findGlyph(n)) is not None
                )
            if key in {"range_start", "range_end"}:
                value = attributes.get(key)
                if expectedType is int and isinstance(value, str):
                    value = converters.toDecimal(value)
                elif expectedType is str and isinstance(value, int):
                    value = converters.toUniHex(value)
            if isinstance(value, expectedType):
                return value
        return None
