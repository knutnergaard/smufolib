# pylint: disable=C0114
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Type
from collections.abc import Iterator

from smufolib.request import Request
from smufolib import config
from smufolib.utils import converters, error, normalizers
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
NAMES_LIB_KEY = "com.smufolib.names"

RangeValue = str | int | tuple["Glyph", ...] | None
T = TypeVar("T", bound=RangeValue)


class Range:
    """SMuFL range-related metadata.

    This object provides access to metadata describing how a :class:`.Glyph` relates to
    SMuFL-defined glyph ranges. Specified range data is sourced from
    :confval:`metadata.paths.ranges`, falling back to
    :confval:`metadata.fallbacks.ranges` if the former is unavailable.

    Like :class:`.Font` or :class:`.Layer`, this object behaves like a collection of
    :class:`.Glyph` instances. However, membership checks are based on
    :attr:`.Smufl.name` rather than :attr:`Glyph.name <fontParts.base.BaseGlyph.name>`.

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
        """Check if the range is valid.

        A range is considered valid if it has a name, a start, and an end Unicode value.

        """
        return self.name is not None and self.start is not None and self.end is not None

    def __eq__(self, other: object) -> bool:
        """Check if two ranges are equal.

        Two ranges are considered equal if they have the same name, start, and end
        Unicode values.

        :param other: The other object to compare with.

        """
        return (
            isinstance(other, Range)
            and self.name == other.name
            and self.start == other.start
            and self.end == other.end
        )

    def __hash__(self) -> int:
        return hash((self.name, self.start, self.end))

    # -----------------
    # Glyph Interaction
    # -----------------

    def __contains__(self, name: str) -> bool:
        """Check if a glyph name is part of the range.

        :param name: The :attr:`.Smufl.name` of the glyph to check.

        """
        glyphNames = self._getAttribute("glyphNames", tuple)
        return name in glyphNames if glyphNames else False

    def __getitem__(self, name: str) -> Glyph:
        """Get a SMuFL glyph by its canonical name from the range.

        :param name: The :attr:`.Smufl.name` of the glyph to retrieve.
        :raises TypeError: If `name` or `glyph` is not of the expected type.
        :raises ValueError: If `name` is not a valid SMuFL name.
        :raises KeyError: If the glyph is not found.

        Example:

            >>> glyph = range["accidentalFlat"]  # doctest: +ELLIPSIS
            <Glyph 'uniE260' ['accidentalFlat'] ('public.default') at ...>

        """
        if self._smufl is not None:
            glyph = self._smufl[name]

            if (
                glyph is not None
                and glyph.unicode is not None
                and self.start <= glyph.unicode <= self.end
            ):
                return glyph

        raise KeyError(error.generateErrorMessage("missingGlyph", name=name))

    def __setitem__(self, name: str, glyph: Glyph) -> None:
        """Insert or replace a SMuFL glyph in the range.

        If `glyph` is considered recommended (i.e., listed in
        :confval:`metadata.glyphnames`), it will be assigned a corresponding
        :attr:`~fontParts.base.BaseGlyph.name` and
        :attr:`~fontParts.base.BaseGlyph.unicode`.

        If it is optional or not a SMUFL glyph, `name` will be used if ``glyph.name`` is
        :obj:`None`.

        :param name: The :attr:`.Smufl.name` of the glyph to insert or replace.
        :param glyph: The :class:`.Glyph` object to insert.
        :raises TypeError: If `name` or `glyph` is not of the expected type.
        :raises ValueError:
            - If `name` is not a valid SMuFL name.
            - If `glyph` is not within the range's Unicode range.

        Example:

            >>> range["accidentalFlat"] = glyph

        """
        if self._smufl is None or self.font is None:
            return

        self._smufl[name] = glyph

        inserted = self._smufl[name]

        if (
            inserted is None
            or inserted.unicode is None
            or not self.start <= inserted.unicode <= self.end
        ):
            del self[name]
            raise ValueError(
                error.generateErrorMessage(
                    "unicodeOutOfRange",
                    objectName=name,
                    start=self.strStart,
                    end=self.strEnd,
                )
            )

    def __delitem__(self, name: str) -> None:
        """Delete a SMuFL glyph from the range.

        :param name: The :attr:`.Smufl.name` of the glyph to delete.
        :raises KeyError: If the glyph does not exist in the range.

        Example:

            >>> del range["accidentalFlat"]

        """
        if self._smufl is not None:
            del self._smufl[name]

    def __iter__(self) -> Iterator[Glyph]:
        return iter(self.glyphs or ())

    def __len__(self) -> int:
        return len(self.glyphs) if self.glyphs is not None else 0

    def keys(self):
        """Return a view of the canonical SMuFL glyph names in the range."""
        names = _lib.getLibSubdict(self.font, NAMES_LIB_KEY)
        filtered = {k: v for k, v in names.items() if k in self}
        return filtered.keys()

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
            if key == "glyphNames":
                value = tuple(attributes["glyphs"])
            if key == "glyphs":
                value = tuple(
                    self._smufl[n]
                    for n in attributes[key]
                    if n in self._smufl and self._smufl[n] is not None
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
