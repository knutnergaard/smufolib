# pylint: disable=C0103, C0114, R0904, W0212, W0221
from __future__ import annotations
from typing import TYPE_CHECKING, cast, Any
from collections.abc import Iterator
import re
import warnings

from fontParts.base.base import BaseObject

from smufolib import config
from smufolib.objects.range import Range, METADATA, RANGES_LIB_KEY
from smufolib.objects.engravingDefaults import EngravingDefaults
from smufolib.objects import _lib
from smufolib.request import Request
from smufolib.utils import converters, error, normalizers

if TYPE_CHECKING:  # pragma: no cover
    from smufolib.objects.layer import Layer
    from smufolib.objects.font import Font
    from smufolib.objects.glyph import Glyph

CONFIG = config.load()
EDITABLE_RANGES = CONFIG["ranges"]["editable"]
STRICT_CLASSES = CONFIG["classes"]["strict"]
CLASSES_LIB_KEY = "com.smufolib.classes"
DESCRIPTION_LIB_KEY = "com.smufolib.description"
DESIGN_SIZE_LIB_KEY = "com.smufolib.designSize"
NAMES_LIB_KEY = "com.smufolib.names"
NAME_LIB_KEY = "com.smufolib.name"
SIZE_RANGE_LIB_KEY = "com.smufolib.sizeRange"
SPACES_LIB_KEY = "com.smufolib.spaces"
GLYPHNAMES_DATA = Request.glyphnames()

#: Names of glyph anchors specified by the SMuFL standard.
ANCHOR_NAMES: set[str] = {
    "splitStemUpSE",
    "splitStemUpSW",
    "splitStemDownNE",
    "splitStemDownNW",
    "stemUpSE",
    "stemDownNW",
    "stemUpNW",
    "stemDownSW",
    "nominalWidth",
    "numeralTop",
    "numeralBottom",
    "cutOutNE",
    "cutOutSE",
    "cutOutSW",
    "cutOutNW",
    "graceNoteSlashSW",
    "graceNoteSlashNE",
    "graceNoteSlashNW",
    "graceNoteSlashSE",
    "repeatOffset",
    "noteheadOrigin",
    "opticalCenter",
}

#: Names of glyph classes included in the SMuFL specification.
CLASS_NAMES: set[str] = {
    "accidentals",
    "accidentals24EDOArrows",
    "accidentals53EDOTurkish",
    "accidentals72EDOWyschnegradsky",
    "accidentalsAEU",
    "accidentalsArabic",
    "accidentalsHelmholtzEllis",
    "accidentalsJohnston",
    "accidentalsPersian",
    "accidentalsSagittalAthenian",
    "accidentalsSagittalDiacritics",
    "accidentalsSagittalMixed",
    "accidentalsSagittalPromethean",
    "accidentalsSagittalPure",
    "accidentalsSagittalTrojan",
    "accidentalsSims",
    "accidentalsStandard",
    "accidentalsSteinZimmermann",
    "accidentalsStockhausen",
    "articulations",
    "articulationsAbove",
    "articulationsBelow",
    "combiningStaffPositions",
    "clefs",
    "clefsC",
    "clefsF",
    "clefsG",
    "dynamics",
    "forTextBasedApplications",
    "multiGlyphForms",
    "noteheads",
    "noteheadSetCircled",
    "noteheadSetCircleX",
    "noteheadSetDefault",
    "noteheadSetDiamond",
    "noteheadSetDiamondOld",
    "noteheadSetHeavyX",
    "noteheadSetLargeArrowDown",
    "noteheadSetLargeArrowUp",
    "noteheadSetNamesPitch",
    "noteheadSetNamesSolfege",
    "noteheadSetPlus",
    "noteheadSetRoundLarge",
    "noteheadSetRoundSmall",
    "noteheadSetSacredHarp",
    "noteheadSetSlashed1",
    "noteheadSetSlashed2",
    "noteheadSetSlashHorizontalEnds",
    "noteheadSetSlashVerticalEnds",
    "noteheadSetSquare",
    "noteheadSetTriangleDown",
    "noteheadSetTriangleLeft",
    "noteheadSetTriangleRight",
    "noteheadSetTriangleUp",
    "noteheadSetWithX",
    "noteheadSetX",
    "parenthesesNotehead",
    "octaves",
    "ornaments",
    "pauses",
    "pausesAbove",
    "pausesBelow",
    "rests",
    "stemDecorations",
    "wigglesArpeggiato",
    "wigglesArpeggiatoDown",
    "wigglesArpeggiatoUp",
    "wigglesCircularMotion",
    "wigglesQuasiRandom",
    "wigglesTrill",
    "wigglesVibrato",
    "wigglesVibratoVariable",
}


#: Names of font-specific attributes of the :class:`Smufl` class.
FONT_ATTRIBUTES: set[str] = {"designSize", "engravingDefaults", "sizeRange", "spaces"}

#: Names of glyph-specific attributes of the :class:`Smufl` class.
GLYPH_ATTRIBUTES: set[str] = {"classes", "description", "name"}


class Smufl(BaseObject):
    """SMuFL metadata interface for fonts and glyphs.

    This class provides structured access to SMuFL-related metadata and utility methods
    for interacting with both font-level and glyph-level data. It may be accessed from
    either a :class:`.Font` or a :class:`.Glyph`. Font-level attributes are available
    in both cases, thanks to consistent parent access patterns in FontParts.

    .. _about-glyph-naming:
    .. admonition:: About Glyph Naming

        Attributes dealing with ligatures (:attr:`isLigature`, :attr:`componentGlyphs`,
        :attr:`componentNames`) and stylistic alternates (:attr:`isSalt`, :attr:`isSet`,
        :attr:`alternates`, :attr:`base`, and :attr:`suffix`) depend on strict adherence
        to the descriptive naming schemes stipulated in the `Adobe Glyph List
        Specification <https://github.com/adobe-type-tools/agl-specification#readme>`_,
        and followed by the SMuFL standard (see `Section 6
        <https://github.com/adobe-type-tools/agl-specification#6-assigning-glyph-names-
        in-new-fonts>`_ for more information).

    .. tip::

        To avoid having to set all the glyph identification attributes manually, it is
        advisable to run the script :mod:`.importID` prior to using this class with an
        existing font for the first time.

    :keyword font: Parent :class:`.Font` object.
    :keyword glyph: Parent :class:`.Glyph` object.

    This object is typically accessed through a :class:`.Font` or :class:`.Glyph`:

        >>> smufl = font.smufl
        >>> glyph = font["uniE050"]
        >>> smufl = glyph.smufl

    It may also be instantiated independently and assigned to a font or glyph later:

        >>> smufl = Smufl()  # doctest: +SKIP

    """

    def _init(self, font: Font | None = None, glyph: Glyph | None = None) -> None:
        self._font = font
        self._glyph = glyph

    def _reprContents(self) -> list[str]:
        contents = []
        if self._glyph is not None:
            contents.append("in glyph")
            contents += self._glyph._reprContents()
        if self._font is not None:
            contents.append("in font")
            contents += self._font._reprContents()
        return contents

    def naked(self):
        """Return the wrapped defcon object.

        This method is useful if you need to bypass the wrapper and interact directly
        with the underlying `defcon <https://defcon.robotools.dev/en/stable/>`_ object
        (e.g., for compatibility with other libraries).

        Example:

            >>> smufl.glyph.naked()  # doctest: +ELLIPSIS
            <defcon.objects.glyph.Glyph object at 0x...>

        """
        return self

    def _requireGlyphAccess(self, attribute: str) -> Glyph | None:
        attribute = f"{self.__class__.__name__}.{attribute}"
        if self._font is not None and self._glyph is None:
            raise AttributeError(
                error.generateErrorMessage(
                    "contextualAttributeError",
                    attribute=attribute,
                    context="accessed from 'Font'",
                )
            )
        return self._glyph

    # -----------------
    # Glyph Interaction
    # -----------------

    def __contains__(self, name: str) -> bool:
        """Check if a SMuFL glyph exists in the font by its canonical name.

        :param name: The :attr:`name` of the glyph to check.

        """
        return name in self._names

    def __getitem__(self, name: str) -> Glyph:
        """Get a SMuFL glyph by its canonical name from the font.

        :param name: The :attr:`name` of the glyph to retrieve.
        :raises TypeError: If `name` or `glyph` is not of the expected type.
        :raises ValueError: If `name` is not a valid SMuFL name.
        :raises KeyError: If the glyph is not found.

        Example:

            >>> glyph = font.smufl["accidentalFlat"]  # doctest: +ELLIPSIS
            <Glyph 'uniE260' ['accidentalFlat'] ('public.default') at ...>

        """
        if self.font is None or name not in self._names:
            raise KeyError(error.generateErrorMessage("missingGlyph", name=name))

        glyphName = self._names[name]
        return self.font[glyphName]

    def __setitem__(self, name: str, glyph: Glyph) -> None:
        """Insert or replace a SMuFL glyph in the font.

        If `glyph` is considered recommended (i.e., listed in
        :confval:`metadata.glyphnames`), it will be assigned a corresponding
        :attr:`~fontParts.base.BaseGlyph.name` and
        :attr:`~fontParts.base.BaseGlyph.unicode`.

        If `glyph` is optional, `name` will be used if ``glyph.name`` is :obj:`None`.

        :param name: The :attr:`name` of the glyph to insert or replace.
        :param glyph: The :class:`.Glyph` object to insert.
        :raises TypeError: If `name` or `glyph` is not of the expected type.
        :raises ValueError:
            - If `name` is not a valid SMuFL name.
            - If ``glyph`` is not a SMuFL glyph (i.e., ``glyph.unicode`` is outside the
            Unicode range U+E000-U+F8FF).

        Example:

            >>> font.smufl["accidentalFlat"] = glyph

        """
        if self.font is None:
            return

        from smufolib.objects.glyph import Glyph

        error.validateType(name, str, objectName="name")
        error.validateType(glyph, Glyph, objectName="glyph")

        normalizedName = cast(str, normalizers.normalizeSmuflName(name, "name"))
        if isinstance(GLYPHNAMES_DATA, dict):
            glyphData = GLYPHNAMES_DATA.get(normalizedName)
        else:
            glyphData = None

        if glyphData:
            glyphName = converters.toUniName(glyphData["codepoint"])
            codepoint = converters.toDecimal(glyphData["codepoint"])
        else:
            glyphName = glyph.name or name
            codepoint = glyph.unicode

        start, end = 0xE000, 0xF8FF
        if codepoint is not None and not start <= codepoint <= end:
            raise ValueError(
                error.generateErrorMessage(
                    "unicodeOutOfRange",
                    objectName=name,
                    start=converters.toUniHex(start),
                    end=converters.toUniHex(end),
                )
            )

        insert = self.font._insertGlyph(glyph, name=glyphName, clear=False)
        insert.unicode = codepoint
        insert.smufl.name = name

    def __delitem__(self, name: str) -> None:
        """Delete a SMuFL glyph from the font.

        :param name: The :attr:`name` of the glyph to delete.
        :raises TypeError: If `name` is not a :class:`str`.
        :raises ValueError: If `name` is not a valid SMuFL name.

        Example:

            >>> del font.smufl["accidentalFlat"]

        """
        if self.font is None or self._names is None:
            return

        normalizedName = normalizers.normalizeSmuflName(name, "Smufl.name")
        if normalizedName in self._names:
            del self.font[self._names[normalizedName]]
            _lib.updateLibSubdictValue(self.font, NAMES_LIB_KEY, normalizedName, None)

    def __len__(self) -> int:
        """Return the number of SMuFL glyphs in the font."""
        if self.font is None or self._names is None:
            return 0
        return len(self._names)

    def __iter__(self) -> Iterator[Glyph]:
        """Iterate over SMuFL glyphs in the font."""
        for smuflName in self._names:
            yield self[smuflName]

    def keys(self):
        """Return a view of the canonical SMuFL glyph names in the font."""
        return self._names.keys()

    def newGlyph(self, name: str, clear: bool = True) -> Glyph | None:
        """Create a new glyph in the font and return it.

        This method is a SMuFL-specific implementation of :meth:`Font.newGlyph
        <fontParts.base.BaseFont.newGlyph>`.

        If `name` represents a recommended glyph (i.e., listed in
        :confval:`metadata.glyphnames`), it will be assigned a corresponding
        :attr:`~fontParts.base.BaseGlyph.name` and
        :attr:`~fontParts.base.BaseGlyph.unicode`. Otherwise, `name` will be used if
        ``glyph.name`` is :obj:`None`.

        :param name: The name of the glyph to create.
        :param clear: Whether to clear any preexisting glyph with the specified `name`
            before creation. Defaults to :obj:`True`
        :returns: The newly created :class:`BaseGlyph` instance.

        Example::

            >>> glyph = font.smufl.newGlyph("brace")

        """
        if self.font is None:
            return None

        normalizedName = cast(str, normalizers.normalizeSmuflName(name, "name"))
        if isinstance(GLYPHNAMES_DATA, dict):
            glyphData = GLYPHNAMES_DATA.get(normalizedName)
        else:
            glyphData = None

        tempName = "com.smufolib.temp"
        if name in self:
            if not clear:
                return self[name]
            del self[name]
        glyph = self.font._newGlyph(tempName)

        if glyphData:
            glyphName = converters.toUniName(glyphData["codepoint"])
            codepoint = converters.toDecimal(glyphData["codepoint"])
        else:
            glyphName = name
            codepoint = None

        glyph.name = glyphName
        glyph.smufl.name = name
        glyph.unicode = codepoint

        return glyph

    # TODO: Remove in v0.8.0
    def findGlyph(self, name: str) -> Glyph | None:
        """Find :class:`.Glyph` object from :attr:`name`.

        .. deprecated 0.7.0

            Use ``font.smufl["name"]`` instead.

        :param name: SMuFL-specific canonical glyph name.

        Example:

            >>> font.smufl.findGlyph("accidentalFlat")  # doctest: +ELLIPSIS
            <Glyph 'uniE260' ['accidentalFlat'] ('public.default') at ...>

        """
        warnings.warn(
            error.generateErrorMessage(
                "deprecated",
                "deprecatedReplacement",
                objectName="findGlyph",
                replacement="__getitem__",
                version="0.7.0",
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        if name is None:
            return None

        normalizedName = normalizers.normalizeSmuflName(name, "Smufl.name")

        if (
            self.font is None
            or self._names is None
            or normalizedName not in self._names
        ):
            return None

        return self.font[self._names[normalizedName]]

    # -------
    # Parents
    # -------

    @property
    def font(self) -> Font | None:
        """The parent :class:`.Font` object.

        Example:

            >>> smufl.font  # doctest: +ELLIPSIS
            <Font 'MyFont Regular' path='/path/to/MyFont.ufo' at ...>

        """
        if self._font is not None:
            return self._font
        if self._glyph is not None:
            return self._glyph.font
        return None

    @font.setter
    def font(self, value: Font) -> None:
        if self._font is not None and self._font != value:
            raise AssertionError(
                "Font for Smufl object is already set and is not same as value."
            )
        if self._glyph is not None:
            raise AssertionError("Glyph for Smufl object is already set.")
        self._font = normalizers.normalizeFont(value)

    @property
    def glyph(self) -> Glyph | None:
        """The parent :class:`.Glyph` object.

        Example:

            >>> smufl.glyph  # doctest: +ELLIPSIS
            <Glyph 'uniE050' ['gClef'] ('public.default') at ...>

        """
        if self._glyph is None:
            return None
        return self._glyph

    @glyph.setter
    def glyph(self, value: Glyph) -> None:
        if self._font is not None:
            raise AssertionError("Font for Smufl object is already set.")
        if self._glyph is not None and self._glyph != value:
            raise AssertionError(
                "Glyph for Smufl object is already set and is not same as value."
            )
        self._glyph = normalizers.normalizeGlyph(value)

    @property
    def layer(self) -> Layer | None:
        """The parent :class:`.Layer` object.

        This property is read-only.

        Example:

            >>> smufl.layer  # doctest: +ELLIPSIS
            <Layer 'public.default' at ...>

        """
        if self._glyph is None:
            return None
        return self._glyph.layer

    # -------------
    # Font Metadata
    # -------------

    @property
    def designSize(self) -> int | None:
        """The optimum point size in integral decipoints.

        Example:

            >>> font.smufl.designSize = 20
            >>> font.smufl.designSize
            20

        """
        if self.font is None:
            return None
        return self.font.lib.naked().get(DESIGN_SIZE_LIB_KEY, None)

    @designSize.setter
    def designSize(self, value: int | None) -> None:
        _lib.updateLibSubdict(
            self.font, DESIGN_SIZE_LIB_KEY, normalizers.normalizeDesignSize(value)
        )

    @property
    def engravingDefaults(self) -> EngravingDefaults:
        """The font's :class:`.EngravingDefaults` object.

        :raises AttributeError: If attempting to access attribute from glyph.

        Example:

            >>> font.smufl.engravingDefaults  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
            <EngravingDefaults in font 'MyFont Regular' path='/path/to/MyFont.ufo'
            auto=True at ...>

        """
        if self.font is None:
            raise AttributeError(
                error.generateErrorMessage(
                    "contextualAttributeError",
                    attribute="Smufl.engravingDefaults",
                    context="'Smufl.font' is None",
                )
            )
        return EngravingDefaults(self)

    @engravingDefaults.setter
    def engravingDefaults(self, value: EngravingDefaults) -> None:
        self.engravingDefaults.update(normalizers.normalizeEngravingDefaults(value))

    @property
    def sizeRange(self) -> tuple[int, int] | None:
        """The optimum size range in integral decipoints.

        Example:

            >>> font.smufl.sizeRange = (16, 24)
            >>> font.smufl.sizeRange
            (16, 24)

        """
        if self.font is None:
            return None
        return self.font.lib.naked().get(SIZE_RANGE_LIB_KEY, None)

    @sizeRange.setter
    def sizeRange(self, value: tuple[int, int] | None) -> None:
        _lib.updateLibSubdict(
            self.font, SIZE_RANGE_LIB_KEY, normalizers.normalizeSizeRange(value)
        )

    # --------------
    # Glyph metadata
    # --------------

    # Alternates

    @property
    def alternates(self) -> tuple[dict[str, str], ...] | None:
        """Alternates of the current glyph as metadata stubs.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE050"] # gClef
            >>> glyph.smufl.alternates
            ({'codepoint': 'U+F472', 'name': 'gClefSmall'},)

        """
        if self.font is None:
            return None

        results = self._findAlternates("Smufl.alternates")
        alternates = []
        for name in results:
            glyph = self.font[name]
            alternates.append(
                {"codepoint": glyph.smufl.codepoint, "name": glyph.smufl.name}
            )
        return tuple(alternates)

    @property
    def alternateGlyphs(self) -> tuple[Glyph, ...] | None:
        """Alternates of the current glyph as :class:`.Glyph` objects.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE050"]
            >>> glyph.smufl.alternateGlyphs  # doctest: +ELLIPSIS
            (<Glyph 'uniE050.ss01' ['gClefSmall'] ('public.default') at ...>,)

        """
        if self.font is None:
            return None

        alternates = self._findAlternates("Smufl.alternateGlyphs")
        return tuple(self.font[a] for a in alternates)

    @property
    def alternateNames(self) -> tuple[str, ...] | None:
        """Alternates of the current glyph by :attr:`name`.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE050"]
            >>> glyph.smufl.alternateNames
            ('gClefSmall',)

        """
        if self.font is None:
            return None

        alternates = self._findAlternates("Smufl.alternateNames")
        return tuple(self.font[a].smufl.name for a in alternates)

    def _findAlternates(self, attribute: str) -> list[str]:
        # find alt names among string of glyph names
        glyph = self._requireGlyphAccess(attribute)
        if glyph is None or self.font is None:
            return []

        string = " ".join(sorted(self.font.keys()))
        pattern = rf"\b{glyph.name}\.(?:s?alt|ss)[0-9]{{2}}\b"
        return re.findall(pattern, string)

    @property
    def base(self) -> Glyph | None:
        """Base glyph of the current glyph.

        If the current glyph is not an alternate (i.e., a stylistic variant),
        the glyph itself is returned.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE050.ss01"]  # doctest: +ELLIPSIS
            >>> glyph.smufl.base
            <Glyph 'uniE050' ['gClef'] ('public.default') at ...>

        """
        if self.font is None:
            return None

        baseName = self._getBasename()
        if self.font and baseName:
            return self.font[baseName]
        return None

    def _getBasename(self) -> str | None:
        # Get name of base glyph.
        glyph = self._requireGlyphAccess("base")
        if self.font is None or glyph is None or glyph.name is None:
            return None
        basename = glyph.name.split(".")[0]
        return basename if basename in self.font else None

    @property
    def suffix(self) -> str | None:
        """Suffix of the current glyph.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE050.ss01"]
            >>> glyph.smufl.suffix
            'ss01'

        """
        if self.font is None:
            return None

        glyph = self._requireGlyphAccess("suffix")
        if glyph is not None and (self.isSalt or self.isSet):
            return glyph.name.split(".")[1]
        return None

    # Components

    @property
    def componentGlyphs(self) -> tuple[Glyph, ...] | None:
        """Ligature components by :class:`.Glyph` object.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> ligature = font["uniE26A_uniE260_uniE26B"]
            >>> ligature.smufl.componentGlyphs  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
            (<Glyph 'uniE26A' ['accidentalParensLeft'] ('public.default') at ...>,
            <Glyph 'uniE260' ['accidentalFlat'] ('public.default') at ...>,
            <Glyph 'uniE26B' ['accidentalParensRight'] ('public.default') at ...>)

        """
        glyph = self._requireGlyphAccess("componentGlyphs")
        if glyph is None or self.font is None:
            return None

        if not self.isLigature:
            return ()

        components = [self.font[n] for n in glyph.name.split("_") if n in self.font]
        return tuple(components)

    @property
    def componentNames(self) -> tuple[str | None, ...] | None:
        """Ligature components by :attr:`name`.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> ligature = font["uniE26A_uniE260_uniE26B"]
            >>> ligature.smufl.componentNames
            ('accidentalParensLeft', 'accidentalFlat', 'accidentalParensRight')

        """
        glyph = self._requireGlyphAccess("componentGlyphs")
        if glyph is None or self.font is None:
            return None

        if not self.isLigature:
            return ()

        components = [
            self.font[n].smufl.name for n in glyph.name.split("_") if n in self.font
        ]
        return tuple(components)

    # Ranges

    def newRange(
        self,
        name: str,
        start: int,
        end: int,
        description: str,
        overrideExisting: bool = False,
    ) -> None:
        """Add SMuFL range to font.

        This method defines a SMuFL range in the font's metadata using a `start` and
        `end` decimal codepoint.

        The `glyphs` key in the resulting metadata is computed dynamically and reflects
        the current glyphs in the font that fall within the specified range. It will
        update automatically as glyphs are added (and assigned a :attr:`name`) or
        removed.


        :param name: A unique identifier for the range.
        :param start: The starting unicode codepoint of the range.
        :param end: The ending unicode codepoint of the range.
        :param description: A human-readable description of the range.
        :param overrideExisting: Whether to replace an existing range if any part of the
            new range overlap with it. Defaults to :obj:`False`.
        :raises PermissionError: If :confval:`ranges.editable` is disabled.
        :raises ValueError: If `start` or `end` partially or completely overlap with an
            existing range when `overrideExisting` is :obj:`False`.

        Example:

            >>> font.smufl.newRange(  # doctest: +SKIP
            ...     "myRange", 0xF500, 0xF50F, "A Range of custom glyphs."
            ... )


        """
        if self.font is None:
            return

        if not EDITABLE_RANGES:
            raise PermissionError(
                error.generateErrorMessage(
                    "permissionError",
                    context="Editing range data is disallowed in configuration",
                )
            )

        normalizedName = normalizers.normalizeSmuflName(name, "Range.name")
        if normalizedName is None:
            raise TypeError(
                error.generateTypeError(validTypes=str, objectName="name", value=name)
            )
        normalizedDescription = normalizers.normalizeDescription(
            description, "Range.description"
        )

        range_: dict[str, dict[str, str | int | list[str] | None]] = {
            normalizedName: {
                "description": normalizedDescription,
                "range_start": start,
                "range_end": end,
            }
        }

        if self.ranges and (
            any(
                self._hasOverlap((start, end), (r.start, r.end))
                for r in self.ranges
                if r.start and r.end
            )
            and overrideExisting is False
        ):
            raise ValueError(
                error.generateErrorMessage(
                    "overlappingRange",
                    string="Set overrideExisting=True to replace",
                    name=name,
                    start=converters.toUniHex(start),
                    end=converters.toUniHex(end),
                )
            )
        glyphs: list[str] = [
            g.smufl.name
            for g in self.font
            if g.smufl.name and start <= g.unicode <= end
        ]
        range_[normalizedName]["glyphs"] = glyphs
        _lib.updateLibSubdict(self.font, RANGES_LIB_KEY, range_)

    @property
    def ranges(self) -> tuple[Range, ...] | None:
        """SMuFL ranges covered by font or glyph.

        This property behaves differently depending on the context in which the
        :class:`Smufl` object is used:

        - When accessed from a :class:`.Font`, (e.g., ``font.smufl.ranges``) it returns
          a :class:`tuple` of all :class:`.Range` objects covered by the font.
        - When accessed from a :class:`.Glyph` (e.g., ``glyph.smufl.ranges``), it
          returns a singleton :class:`tuple` containing the glyph's corresponding
          :class:`.Range` object.

        This property is read-only.

        Examples:

            >>> font.smufl.ranges  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
            (<Range 'clefs' (U+E050-U+E07F) editable=False at ...>,
            ...
            <Range 'multiSegmentLines' (U+EAA0-U+EB0F) editable=False at ...>)

            >>> glyph = font["uniE050"]
            >>> glyph.smufl.ranges
            (<Range 'clefs' (U+E050-U+E07F) editable=False at ...>,)

        """
        if self.font is None:
            return None

        if self._glyph is not None:
            internalData = _lib.getLibSubdict(self.font, RANGES_LIB_KEY)
            if internalData:
                for data in internalData.values():
                    if self._glyph.unicode is not None and (
                        data.get("range_start")
                        <= self._glyph.unicode
                        <= data.get("range_end")
                    ):
                        return (Range(self, _internal=True),)
            range_ = Range(self, _internal=False)
            return (range_,) if range_ else ()
        return self._collectAllRanges()

    def _getRangesFromMetadata(self, metadata, _internal=False) -> list[Range]:
        if (
            self.font is None
            or self._names is None
            or metadata is None
            or isinstance(metadata, str)
        ):
            return []
        ranges = []
        for data in metadata.values():
            match = next(
                (
                    self._names[smuflName]
                    for smuflName in data["glyphs"]
                    if smuflName in self._names
                ),
                None,
            )
            if match:
                ranges.append(Range(self.font[match].smufl, _internal=_internal))

        return ranges

    def _collectAllRanges(self) -> tuple[Range, ...]:
        internalRanges = (
            self._getRangesFromMetadata(
                _lib.getLibSubdict(self.font, RANGES_LIB_KEY), _internal=True
            )
            or []
        )
        externalRanges = self._getRangesFromMetadata(METADATA) or []
        internalSpans = [
            (r.start, r.end)
            for r in internalRanges
            if r.start is not None and r.end is not None
        ]
        nonConflictingExternal = [
            r
            for r in externalRanges
            if r.start is not None
            and r.end is not None
            and not any(
                self._hasOverlap((r.start, r.end), (iStart, iEnd))
                for iStart, iEnd in internalSpans
            )
        ]
        return tuple(
            sorted(
                internalRanges + nonConflictingExternal,
                key=lambda r: (r.start is None, r.start),
            )
        )

    @staticmethod
    def _hasOverlap(range1: tuple[int, int], range2: tuple[int, int]) -> bool:
        start1, end1 = range1
        start2, end2 = range2
        return not (end1 < start2 or start1 > end2)

    # Anchors

    @property
    def anchors(self) -> dict[str, tuple[int | float, int | float]] | None:
        """SMuFL-specific glyph anchors as Cartesian coordinates.

        This property is read-only. Use the :attr:`Glyph.anchors
        <fontParts.base.BaseGlyph.anchors>` attribute to set glyph anchors.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE240"]
            >>> glyph.smufl.anchors  # doctest: +NORMALIZE_WHITESPACE
            {'graceNoteSlashNE': (321, -199),
            'graceNoteSlashSW': (-161, -614),
            'stemUpNW': (0, -10)}

        """
        glyph = self._requireGlyphAccess("anchors")
        if glyph is None:
            return None

        anchors = {}
        for a in glyph.naked().anchors:
            if a.name in ANCHOR_NAMES:
                x = self.toSpaces(a.x) if self.spaces else a.x
                y = self.toSpaces(a.y) if self.spaces else a.y

                if x is None or y is None:
                    return None

                anchors[a.name] = (x, y)

        return anchors

    # Codepoint

    @property
    def codepoint(self) -> str | None:
        """Unicode codepoint as formatted string.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE050"]
            >>> glyph.smufl.codepoint
            'U+E050'

        """
        glyph = self._requireGlyphAccess("codepoint")
        if glyph is None:
            return None

        if not glyph.unicode:
            return None
        return converters.toUniHex(glyph.unicode)

    @codepoint.setter
    def codepoint(self, value: str | None) -> None:
        glyph = self._requireGlyphAccess("codepoint")
        if glyph is not None:
            if value is None:
                glyph.unicode = None
            else:
                glyph.unicode = converters.toDecimal(value)

    # Metrics and Dimensions

    @property
    def bBox(self) -> dict[str, tuple[int | float, int | float]] | None:
        """Glyph bounding box as Cartesian coordinates.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE050"]
            >>> glyph.smufl.bBox
            {'bBoxSW': (0, -634), 'bBoxNE': (648, 1167)}

        """
        glyph = self._requireGlyphAccess("bBox")
        if glyph is None:
            return None

        if not glyph.bounds:
            return None
        xMin, yMin, xMax, yMax = glyph.bounds
        if self.spaces:
            xMin, yMin, xMax, yMax = [self.toSpaces(b) for b in glyph.bounds]
        return {"bBoxSW": (xMin, yMin), "bBoxNE": (xMax, yMax)}

    @property
    def advanceWidth(self) -> int | float | None:
        """Glyph advance width.

        This property is equivalent to :attr:`Glyph.width
        <fontParts.base.BaseGlyph.width>`.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE050"]
            >>> glyph.smufl.advanceWidth = 230.5
            >>> glyph.smufl.advanceWidth
            230.5

        """
        glyph = self._requireGlyphAccess("advanceWidth")
        if glyph is None:
            return None

        if self.spaces:
            return self.toSpaces(glyph.width)
        return glyph.width

    @advanceWidth.setter
    def advanceWidth(self, value: int | float) -> None:
        glyph = self._requireGlyphAccess("advanceWidth")
        if glyph is not None:
            if self.spaces:
                normalizedValue = self.toUnits(value)
                if normalizedValue is None:
                    return
            else:
                normalizedValue = value
            glyph.width = normalizedValue

    # --------------
    # Identification
    # --------------

    # Font
    # ----

    # Font family name is accessible through font.smufl.name.

    def classMembers(self, className: str) -> tuple[Glyph, ...]:
        """Return all glyphs in the font that belong to the given SMuFL class.

        .. versionadded:: 0.6.0

        :param className: The name of the SMuFL glyph class to search for.

        Example:

            >>> glyph.smufl.classMembers("accidentalsStandard")  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
            (<Glyph 'uniE260' ['accidentalFlat'] ('public.default') at ...>,
            <Glyph 'uniE266' ['accidentalTripleFlat'] ('public.default') at ...>,
            <Glyph 'uniE267' ['accidentalNaturalFlat'] ('public.default') at ...>)

        """
        if self.font is None:
            return ()
        return tuple(
            sorted(
                [g for g in self.font if className in g.smufl.classes],
                key=lambda g: g.name,
            )
        )

    @property
    def version(self) -> float | None:
        """SMuFL-specific font version number.

        Example:

            >>> font.smufl.version = 2.2
            >>> font.smufl.version
            2.2

        """
        if self.font is None:
            return None
        try:
            return float(
                f"{self.font.info.naked().versionMajor}."
                f"{self.font.info.naked().versionMinor}"
            )
        except ValueError:
            return None

    @version.setter
    def version(self, value: float | None) -> None:
        if value is None:
            major, minor = None, None
        else:
            major, minor = [int(n) for n in str(value).split(".")]
        if self.font is not None:
            self.font.info.naked().versionMajor = major
            self.font.info.naked().versionMinor = minor

    # Glyph
    # -----
    @property
    def classes(self) -> tuple[str, ...] | None:
        """SMuFL-specific class memberships.

        If :confval:`classes.strict` is enabled, only SMuFL-specific class names are
        allowed. See :data:`.CLASS_NAMES` for the full :class:`set` of specified names.

        .. versionadded:: 0.7.0

            Distinction between strict, SMuFL-specific vs. lenient, custom class names.

        :raises AttributeError: If attempting to access attribute from font.
        :raises ValueError: If attempting to set a name not specified in
            :data:`.CLASS_NAMES` when :confval:`classes.strict` is enabled.

        Example::

            >>> glyph = font["uniE260"]
            >>> glyph.smufl.classes
            ('accidentals', 'accidentalsSagittalMixed',
            'accidentalsStandard', 'combiningStaffPositions')

        """
        glyph = self._requireGlyphAccess("classes")
        if glyph is None:
            return None
        return tuple(glyph.lib.naked().get(CLASSES_LIB_KEY, ()))

    @classes.setter
    def classes(self, value: tuple[str, ...] | None) -> None:
        self._requireGlyphAccess("classes")
        if STRICT_CLASSES and value:
            for item in value:
                if item not in CLASS_NAMES:
                    raise ValueError(
                        error.generateErrorMessage(
                            "itemsValueError",
                            objectName="Smufl.classes",
                            value=item,
                            string="Non-SMuFL classes are disallowed in configuration",
                        )
                    )
        _lib.updateLibSubdict(
            self.glyph, CLASSES_LIB_KEY, normalizers.normalizeClasses(value)
        )

    @property
    def description(self) -> str | None:
        """SMuFL-specific human-readable glyph description.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE260"]
            >>> glyph.smufl.description = "Flat"
            >>> glyph.smufl.description
            'Flat'

        """
        glyph = self._requireGlyphAccess("description")
        if glyph is None:
            return None
        return glyph.lib.naked().get(DESCRIPTION_LIB_KEY, None)

    @description.setter
    def description(self, value: str | None) -> None:
        self._requireGlyphAccess("description")
        _lib.updateLibSubdict(
            self.glyph,
            DESCRIPTION_LIB_KEY,
            normalizers.normalizeDescription(value, "Smufl.description"),
        )

    @property
    def name(self) -> str | None:
        """SMuFL-specific canonical font or glyph name.

        This property behaves differently depending on the context in which the
        :class:`Smufl` object is used:

        - When accessed from a :class:`.Font` (``e.g, font.smufl.name``), it returns the
          SMuFL font name, equivalent to ``font.info.familyName``.
        - When accessed from a :class:`.Glyph` (``e.g, glyph.smufl.name``), it returns
          the canonical SMuFL glyph name.

        Examples:

            >>> font.smufl.name = "MyFont"
            >>> font.smufl.name
            'MyFont'

            >>> glyph = font["uniE050"]
            >>> glyph.smufl.name = "gClef"
            >>> glyph.smufl.name
            'gClef'

        """
        if self.font is None:
            return None

        if self.glyph is None:
            return self.font.info.naked().familyName
        return self.glyph.lib.naked().get(NAME_LIB_KEY, None)

    @name.setter
    def name(self, value: str | None) -> None:
        # Update com.smufolib.names before ID property
        if self.font is not None:
            if self._glyph is None:
                self.font.info.naked().familyName = value
            else:
                normalizedName = normalizers.normalizeSmuflName(value, "Smufl.name")
                self._updateRange(normalizedName)
                self._updateNames(normalizedName)
                _lib.updateLibSubdict(
                    self.glyph,
                    NAME_LIB_KEY,
                    normalizedName,
                )

    # TODO: Remove in v0.8.0
    @property
    def names(self) -> dict[str, str] | None:
        """Mapping of canonical SMuFL names to corresponding glyph names.

        .. deprecated:: 0.7.0

        This property is read-only. Its content is updated through the
        :attr:`.Smufl.name` and :attr:`Glyph.name` attributes.

        """
        warnings.warn(
            error.generateErrorMessage(
                "deprecated",
                "deprecatedReplacement",
                objectName="Smufl.names",
                version="0.7",
                replacement="keys",
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        return _lib.getLibSubdict(self.font, NAMES_LIB_KEY)

    @property
    def _names(self) -> dict[str, str]:
        return _lib.getLibSubdict(self.font, NAMES_LIB_KEY) or {}

    def _clearNames(self) -> None:
        if self.font is not None:
            if self.name:
                self._names.pop(self.name, None)
            if not self._names:
                _lib.updateLibSubdict(self.font, NAMES_LIB_KEY, None)

    def _addNames(self, value: Any) -> None:
        if self._glyph is not None:
            if value in self._names and self._names[value] != self._glyph.name:
                raise ValueError(
                    error.generateErrorMessage(
                        "duplicateAttributeValue",
                        value=value,
                        attribute="smufl.name",
                        objectName="Glyph",
                        conflictingInstance=self._names[value],
                    )
                )

            if self._glyph.name in self._names.values():
                filtered = {
                    k: v for k, v in self._names.items() if v != self._glyph.name
                }
                _lib.updateLibSubdict(self.font, NAMES_LIB_KEY, filtered)

            _lib.updateLibSubdictValue(
                self.font, NAMES_LIB_KEY, value, self._glyph.name
            )

    def _updateNames(self, value: str | None) -> None:
        # Keep dynamic dict of glyph names in font.lib.
        if value is None:
            self._clearNames()
        else:
            self._addNames(value)

    def _updateRange(self, value: str | None) -> None:
        # Update name in range.glyphs.
        if not self.font or not self.ranges:
            return

        range_ = self.ranges[0]
        if not range_._internal:
            return

        glyphs = self.font.lib[RANGES_LIB_KEY][range_.name]["glyphs"]
        if self.name in glyphs:
            glyphs.remove(self.name)
        if value is not None:
            glyphs.append(value)

    # ----------
    # Predicates
    # ----------

    @property
    def isLigature(self) -> bool:
        """Return :obj:`True` if glyph is ligature.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> ligature = font["uniE26A_uniE260_uniE26B"]
            >>> ligature.smufl.isLigature
            True
            >>> glyph = font["uniE260"]
            >>> glyph.smufl.isLigature
            False

        """
        glyph = self._requireGlyphAccess("isLigature")
        if (
            glyph is not None
            and glyph.name
            and glyph.name.count("uni") > 1
            and "_" in glyph.name
        ):
            return True
        return False

    @property
    def isMember(self) -> bool:
        """Return :obj:`True` if glyph is either :smufl:`recommended or optional
        <about/recommended-chars-optional-glyphs.html>`.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE050"]
            >>> glyph.smufl.isMember
            True
            >>> glyph = font["space"]
            >>> glyph.smufl.isMember
            False

        """
        glyph = self._requireGlyphAccess("isMember")
        if glyph is not None and glyph.unicode and 0xE000 <= glyph.unicode <= 0xF8FF:
            return True
        return False

    @property
    def isOptional(self) -> bool:
        """Return :obj:`True` if glyph is :smufl:`optional
        <about/recommended-chars-optional-glyphs.html>`.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE050.ss01"]
            >>> glyph.smufl.isOptional
            True
            >>> glyph = font["uniE050"]
            >>> glyph.smufl.isOptional
            False

        """
        glyph = self._requireGlyphAccess("isOptional")
        if glyph is not None and glyph.unicode and 0xF400 <= glyph.unicode <= 0xF8FF:
            return True
        return False

    @property
    def isRecommended(self) -> bool:
        """Return :obj:`True` if glyph is :smufl:`recommended
        <about/recommended-chars-optional-glyphs.html>`.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE050"]
            >>> glyph.smufl.isRecommended
            True
            >>> glyph = font["uniE050.ss01"]
            >>> glyph.smufl.isRecommended
            False

        """
        glyph = self._requireGlyphAccess("isRecommended")
        if glyph is not None and glyph.unicode and 0xE000 <= glyph.unicode <= 0xF3FF:
            return True
        return False

    @property
    def isSalt(self) -> bool:
        """Return :obj:`True` if glyph is stylistic alternate.

        Glyph names with either ``".alt"`` and ``".salt"`` suffix are
        accepted. See :ref:`Note <about-glyph-naming>` about glyph
        naming.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE062.salt01"]
            >>> glyph.smufl.isSalt
            True
            >>> glyph = font["uniE050.ss01"]
            >>> glyph.smufl.isSalt
            False

        """
        glyph = self._requireGlyphAccess("isSalt")
        if (
            glyph is not None
            and glyph.name
            and (
                glyph.name.endswith(".salt", 7, -2)
                or glyph.name.endswith(".alt", 7, -2)
            )
        ):
            return True
        return False

    @property
    def isSet(self) -> bool:
        """Return :obj:`True` if glyph is stylistic set member.

        See :ref:`Note <about-glyph-naming>` about glyph naming.

        This property is read-only.

        :raises AttributeError: If attempting to access attribute from font.

        Example:

            >>> glyph = font["uniE050.ss01"]
            >>> glyph.smufl.isSet
            True
            >>> glyph = font["uniE062.salt01"]
            >>> glyph.smufl.isSet
            False

        """
        glyph = self._requireGlyphAccess("isSet")
        if glyph is not None and glyph.name and glyph.name.endswith(".ss", 7, -2):
            return True
        return False

    # -----------------------------
    # Normalization and Measurement
    # -----------------------------

    def round(self) -> None:
        """Round font units to integers.

        Method applies to the following attributes:

        - :attr:`Smufl.engravingDefaults`
        - :attr:`Smufl.anchors`
        - :attr:`Smufl.advanceWidth`
        - :attr:`Glyph.width <fontParts.base.BaseGlyph.width>`
        - :attr:`Glyph.height <fontParts.base.BaseGlyph.height>`
        - :attr:`Glyph.contours <fontParts.base.BaseGlyph.contours>`
        - :attr:`Glyph.components <fontParts.base.BaseGlyph.components>`
        - :attr:`Glyph.anchors <fontParts.base.BaseGlyph.anchors>`
        - :attr:`Glyph.guidelines <fontParts.base.BaseGlyph.guidelines>`


        If :attr:`spaces` is :obj:`True`, values are left unchanged.

        Examples:

            >>> font.smufl.spaces = True
            >>> glyph.smufl.advanceWidth
            0.922
            >>> glyph.smufl.round()
            >>> glyph.smufl.advanceWidth
            0.922

            >>> font.smufl.spaces = False
            >>> glyph = font["uniE050"]
            >>> glyph.smufl.advanceWidth
            230.5
            >>> glyph.smufl.round()
            >>> glyph.smufl.advanceWidth
            231

        """
        if self.spaces:
            return

        if self.font:
            self.engravingDefaults.round()

        if self._glyph is not None:
            self._glyph.round()

    def toSpaces(self, value: int | float) -> float | None:
        """Convert font units to staff spaces based on font UPM size.

        The inverse of :meth:`toUnits`.

        :param value: Value to convert.

        Example::

            >>> font.info.unitsPerEm = 2048
            >>> font.smufl.toSpaces(512)
            1.0

        """
        if self.font is None:
            return None

        if not self.font.info.unitsPerEm:
            raise AttributeError(
                error.generateErrorMessage(
                    "missingDependency",
                    objectName="value",
                    dependency="font.info.unitsPerEm",
                )
            )

        return converters.convertMeasurement(
            measurement=value,
            targetUnit="spaces",
            unitsPerEm=self.font.info.unitsPerEm,
            rounded=False,
        )

    def toUnits(self, value: int | float, rounded=True) -> int | float | None:
        """Convert staff spaces to font units based on font UPM size.

        The inverse of :meth:`toSpaces`. The result is always rounded.

        :param value: Value to convert.
        :param rounded: Whether to round result to nearest integer.

        Example::

            >>> font.info.unitsPerEm = 2048
            >>> font.smufl.toSpaces(2)
            1024

        """
        if self.font is None:
            return None

        if not self.font.info.unitsPerEm:
            raise AttributeError(
                error.generateErrorMessage(
                    "missingDependency",
                    objectName="value",
                    dependency="font.info.unitsPerEm",
                )
            )

        return converters.convertMeasurement(
            measurement=value,
            targetUnit="units",
            unitsPerEm=self.font.info.unitsPerEm,
            rounded=rounded,
        )

    @property
    def spaces(self) -> bool:
        """Set state of measurement to staff spaces.

        Example:

            >>> glyph = font["uniE050"]
            >>> font.smufl.spaces = True
            >>> glyph.smufl.advanceWidth
            0.922
            >>> font.smufl.spaces = False
            >>> glyph.smufl.advanceWidth
            230.5

        """
        if self.font is None:
            return False
        return self.font.lib.naked().get(SPACES_LIB_KEY, False)

    @spaces.setter
    def spaces(self, value):
        if self.font is not None:
            if not self.font.info.unitsPerEm:
                raise AttributeError(
                    error.generateErrorMessage(
                        "missingDependency",
                        objectName="spaces",
                        dependency="font.info.unitsPerEm",
                    )
                )
            value = normalizers.normalizeBoolean(value)
            if value:
                self.font.lib.naked()[SPACES_LIB_KEY] = True
            else:
                self.font.lib.naked().pop(SPACES_LIB_KEY, False)

    # ------------------------
    # Override from BaseObject
    # ------------------------

    def raiseNotImplementedError(self):
        """This exception needs to be raised frequently by
        the base classes. So, it's here for convenience.

        """
        raise NotImplementedError(  # pragma: no cover
            error.generateErrorMessage(
                "notImplementedError", objectName=self.__class__.__name__
            )
        )
