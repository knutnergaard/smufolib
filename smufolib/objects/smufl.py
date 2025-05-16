# pylint: disable=C0103, C0114, R0904, W0212, W0221
from __future__ import annotations
from typing import TYPE_CHECKING, Any
import re
import warnings

from fontParts.base.base import BaseObject
from smufolib.objects.range import Range, METADATA
from smufolib.objects.engravingDefaults import EngravingDefaults
from smufolib.utils import converters, error, normalizers

if TYPE_CHECKING:  # pragma: no cover
    from smufolib.objects.layer import Layer
    from smufolib.objects.font import Font
    from smufolib.objects.glyph import Glyph

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


#: Names of font-specific attributes of the :class:`Smufl` class.
FONT_ATTRIBUTES: set[str] = {"designSize", "engravingDefaults", "sizeRange", "spaces"}

#: Names of glyph-specific attributes of the :class:`Smufl` class.
GLYPH_ATTRIBUTES: set[str] = {"classes", "description", "name"}


class Smufl(BaseObject):
    """Provide SMuFL-related metadata and functionality.

    This class may be called from either :class:`.Font` or :class:`.Glyph`.
    Font-specific attributes with unique names may be accessed from both, due to the
    consistent access to parent classes in FontParts.

    .. _about-glyph-naming:

    .. admonition:: About Glyph Naming
    
        Attributes dealing with ligatures (:attr:`isLigature`, :attr:`componentGlyphs`,
        :attr:`componentNames`) and stylistic alternates (:attr:`isSalt`, :attr:`isSet`,
        :attr:`alternates`, :attr:`base` and :attr:`suffix`) depend on strict adherence
        to the descriptive naming schemes stipulated in the `Adobe Glyph List
        Specification <https://github.com/adobe-type-tools/agl-\ specification#readme>`_
        and followed by the SMuFL standard (see `Section 6
        <https://github.com/adobe-type-tools/agl-\
        specification#6-assigning-glyph-names-in-new-fonts>`_ for more information).

    .. tip:: To avoid having to set all the glyph identification
       attributes manually, it is advisable to run the
       script :mod:`.importID` prior to using this class with an
       existing font for the first time.

    :param font: Parent :class:`.Font` object.
    :param glyph: Parent :class:`.Glyph` object.

    While this object is normally created as part of a :class:`.Font`, an orphan
    :class:`Smufl` object can be created like this::

        >>> smufl = Smufl()

    """

    def _init(self, font: Font | None = None, glyph: Glyph | None = None) -> None:
        self._font = font
        self._glyph = glyph
        self._layer = None

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
        # BaseObject override for __eq__ and __hash__
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

    def findGlyph(self, name: str) -> Glyph | None:
        """Find :class:`.Glyph` object from :attr:`name`.

        :param name: SMuFL-specific canonical glyph name.

        Example::

            >>> font.smufl.findGlyph("barlineSingle")
            <Glyph 'uniE030' ('public.default') at 4393557200>

        """
        if name is None:
            return None

        normalizedName = normalizers.normalizeSmuflName(name)

        if self.font is None or self.names is None or normalizedName not in self.names:
            return None

        return self.font[self.names[normalizedName]]

    # -------
    # Parents
    # -------

    @property
    def font(self) -> Font | None:
        """Parent :class:`.Font` object.

        Example::

            >>> glyph.smufl.font
            <Font 'MyFont' path='path/to/my/font.ufo' at 4405856720>

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
        """Parent :class:`.Glyph` object.

        Example::

            >>> glyph.smufl.glyph
            <Glyph 'uniE587' ('public.default') at 4536458160>

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
        """Parent :class:`.Layer` object.

        This property is read-only.

        Example::

            >>> glyph.smufl.layer
            <Layer 'public.default' at 4568631952>

        """
        if self._glyph is None:
            return None
        return self._glyph.layer

    # -------------
    # Font Metadata
    # -------------

    @property
    def designSize(self) -> int | None:
        """Optimum point size in integral decipoints.

        Example::

            >>> font.smufl.designSize
            240

        """
        if self.font is None:
            return None
        return self.font.lib.naked().get("com.smufolib.designSize", None)

    @designSize.setter
    def designSize(self, value: int | None) -> None:
        self._updateFontLib(
            "com.smufolib.designSize", normalizers.normalizeDesignSize(value)
        )

    @property
    def engravingDefaults(self) -> EngravingDefaults:
        """Font's :class:`.EngravingDefaults` object.

        Example::

            >>> font.smufl.engravingDefaults
            <EngravingDefaults in font 'MyFont' path='/path/to/myFont.ufo'
            auto=True at 4425372944>

        """
        if self.font is None:
            raise AttributeError(
                error.generateErrorMessage(
                    "contextualAttributeError",
                    attribute=f"{self.__class__.__name__}.engravingDefaults",
                    context=f"'{self.__class__.__name__}.font' is None",
                )
            )
        return EngravingDefaults(self)

    @engravingDefaults.setter
    def engravingDefaults(self, value: EngravingDefaults) -> None:
        if self.engravingDefaults:
            self.engravingDefaults.update(normalizers.normalizeEngravingDefaults(value))

    @property
    def sizeRange(self) -> tuple[int, int] | None:
        """Optimum size range in integral decipoints.

        Example::

            >>> font.smufl.designSize
            (180, 260)

        """
        if self.font is None:
            return None
        return self.font.lib.naked().get("com.smufolib.sizeRange", None)

    @sizeRange.setter
    def sizeRange(self, value: tuple[int, int] | None) -> None:
        self._updateFontLib(
            "com.smufolib.sizeRange", normalizers.normalizeSizeRange(value)
        )

    def _updateFontLib(self, key: str, value: Any) -> None:
        # Common font metadata setter.
        if self.font is not None:
            if value is None:
                self.font.lib.naked().pop(key, None)
            else:
                self.font.lib.naked()[key] = value

    # --------------
    # Glyph metadata
    # --------------

    # Alternates

    @property
    def alternates(self) -> tuple[dict[str, str], ...] | None:
        """Metadata of glyph alternates.

        This property is read-only.

        Example::

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
        """Alternates of base glyph by :class:`.Glyph` object.

        This property is read-only.

        Example::

            >>> glyph.smufl.alternateGlyphs
            (<Glyph 'uniE240.ss02' ('public.default') at 4391369312>,
            <Glyph 'uniE240.ss03' ('public.default') at 4391367776>)

        """
        if self.font is None:
            return None

        alternates = self._findAlternates("Smufl.alternateGlyphs")
        return tuple(self.font[a] for a in alternates)

    @property
    def alternateNames(self) -> tuple[str, ...] | None:
        """Alternates of base glyph by :attr:`name`.

        This property is read-only.

        Example::

            >>> glyph.smufl.alternateGlyphs
            (flag8thUpShort, flag8thUpSmall)

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
        """:class:`.Glyph` object of alternate's base glyph.

        This property is read-only.

        Example::

            >>> glyph = font["uniE050.ss01"]
            >>> glyph.smufl.base
            <Glyph 'uniE050' ('public.default') at 4373577008>

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
        if glyph is None or glyph.name is None:
            return None
        basename = glyph.name[:7]
        return basename if self.font and basename in self.font else None

    @property
    def suffix(self) -> str | None:
        """Return suffix of alternates.

        This property is read-only.

        Example::

            >>> glyph = font["uniE050.ss01"]
            >>> glyph.smufl.suffix
            ss01

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

        Example::

            >>> glyph = font["uniE09E_uniE083_uniE09F_uniE084"]
            >>> glyph.smufl.componentGlyphs
            (<Glyph 'uniE09E' ('public.default') at 4399803376>,
             <Glyph 'uniE083' ('public.default') at 4399803184>,
             <Glyph 'uniE09F' ('public.default') at 4399797952>,
             <Glyph 'uniE084' ('public.default') at 4399797760>)

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

        Example::

            >>> glyph = font["uniE09E_uniE083_uniE09F_uniE084"]
            >>> glyph.smufl.componentNames
            ('timeSigCombNumerator', 'timeSig3',
             'timeSigCombDenominator', 'timeSig4')

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

    # Range

    # TODO: Remove 'range' in 0.6
    @property
    def range(self) -> Range | None:
        """Glyph's :class:`.Range` object.

        .. deprecated:: 0.5.0
            Use :attr:`ranges` instead.

        This property is read-only.

        Example::

            >>> glyph = font["uniE212"] # stemSwished
            >>> glyph.smufl.range
            <Range 'stems' ('U+E210-U+E21F') at 4348391632>

        """
        warnings.warn(
            error.generateErrorMessage(
                "deprecated",
                "deprecatedReplacement",
                objectName="range",
                version=0.5,
                replacement="ranges",
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        if self.font is None:
            return None
        return Range(self)

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

        Example::

            >>> font.smufl.ranges
            (<Range 'stringTechniques' ('U+E610-U+E62F') at 4449982528>,
            <Range 'multiSegmentLines' ('U+EAA0-U+EB0F') at 4449981712>,
            <Range 'harpTechniques' ('U+E680-U+E69F') at 4449981376>, ...)
            >>> glyph = font["uniE212"] # stemSwished
            >>> glyph.smufl.ranges
            (<Range 'stems' ('U+E210-U+E21F') at 4348391632>,)

        """
        if self.font is None:
            return None

        if self._glyph is None:
            return self._getFontRanges()
        return (Range(self),)

    def _getFontRanges(self) -> tuple[Range, ...] | None:
        if (
            self._font is None
            or self.names is None
            or METADATA is None
            or isinstance(METADATA, str)
        ):
            return None

        ranges = []
        for data in METADATA.values():
            match = next(
                (
                    self.names[smuflName]
                    for smuflName in data["glyphs"]
                    if smuflName in self.names
                ),
                None,
            )
            if match:
                ranges.append(Range(self._font[match].smufl))

        return tuple(ranges)

    # Anchors

    @property
    def anchors(self) -> dict[str, tuple[int | float, int | float]] | None:
        """SMuFL-specific glyph anchors as Cartesian coordinates.

        This property is read-only. Use the :attr:`Glyph.anchors
        <fontParts.base.BaseGlyph.anchors>` attribute to set glyph anchors.

        Example::

            >>> glyph = font["uniE0A3"] # noteheadHalf
            >>> glyph.smufl.anchors
            {'cutOutNW': (0.204, 0.296), 'cutOutSE':
            (0.98, -0.3), 'splitStemDownNE': (0.956, -0.3), 'splitStemDownNW':
            (0.128, -0.428), 'splitStemUpSE': (1.108, 0.372), 'splitStemUpSW':
            (0.328, 0.38), 'stemDownNW': (0.0, -0.168), 'stemUpSE': (1.18, 0.168)}

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

        Example::

            >>> glyph = font["uniE0A3"]
            >>> glyph.smufl.codepoint
            U+E0A3

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

        Example::

            >>> glyph.smufl.bBox
            {'bBoxSW': (0.0, -0.5), 'bBoxNE': (1.18, 0.5)}

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

        Example::

            >>> glyph.smufl.advanceWidth
            671

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

    # Font family name is acessible through font.smufl.name.

    def classMembers(self, className: str) -> tuple[Glyph, ...]:
        """Return all glyphs in the font that belong to the given SMuFL class.

        .. versionadded:: 0.6.0

        :param className: The name of the SMuFL glyph class to search for.

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

        Example::

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

        Example::

            >>> glyph = font["uniE354"] # accSagittalSharp7v11kUp
            >>> glyph.smufl.classes
            ('accidentals', 'accidentalsSagittalAthenian', 'combiningStaffPositions')

        """
        glyph = self._requireGlyphAccess("classes")
        if glyph is None:
            return None
        return tuple(glyph.lib.naked().get("com.smufolib.classes", ()))

    @classes.setter
    def classes(self, value: tuple[str, ...] | None) -> None:
        self._requireGlyphAccess("classes")
        self._updateGlyphLib(
            "com.smufolib.classes", normalizers.normalizeClasses(value)
        )

    @property
    def description(self) -> str | None:
        """SMuFL-specific glyph description.

        Example::

            >>> glyph.smufl.description
            Combining swished stem

        """
        glyph = self._requireGlyphAccess("description")
        if glyph is None:
            return None
        return glyph.lib.naked().get("com.smufolib.description", None)

    @description.setter
    def description(self, value: str | None) -> None:
        self._requireGlyphAccess("description")
        self._updateGlyphLib(
            "com.smufolib.description", normalizers.normalizeDescription(value)
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

        Examples::

            >>> font.smufl.name
            Bravura

        ::

            >>> glyph = font["uniE212"]
            >>> glyph.smufl.name
            stemSwished

        """
        if self.font is None:
            return None

        if self.glyph is None:
            return self.font.info.naked().familyName
        return self.glyph.lib.naked().get("com.smufolib.name", None)

    @name.setter
    def name(self, value: str | None) -> None:
        # Update com.smufolib.names before ID property
        if self.font is not None:
            if self.glyph is None:
                self.font.info.naked().familyName = value
            else:
                self._updateNames(normalizers.normalizeSmuflName(value))
                self._updateGlyphLib(
                    "com.smufolib.name", normalizers.normalizeSmuflName(value)
                )

    @property
    def names(self) -> dict[str, str] | None:
        """Mapping of canonical SMuFL names to corresponding glyph names.

        This property is read-only. It's content is updated through the
        :attr:`.Smufl.name` and :attr:`Glyph.name` attributes.

        """
        if self.font is None:
            return None
        return self.font.lib.naked().get("com.smufolib.names")

    @names.setter
    def names(self, value: dict[str, str] | None) -> None:
        self._updateFontLib("com.smufolib.names", value)

    def _updateGlyphLib(self, key: str, value: Any) -> None:
        if self._glyph is not None:
            if not value:
                if key in self._glyph.lib.naked():
                    del self._glyph.lib.naked()[key]
            else:
                self._glyph.lib.naked()[key] = value

    def _clearNames(self) -> None:
        if self.font is not None:
            if self.names and self.name:
                self.names.pop(self.name, None)
            if not self.names:
                self.font.lib.naked().pop("com.smufolib.names", None)

    def _addNames(self, value: Any) -> None:
        if self.names is None:
            self.names = {}
        if self._glyph is not None:
            if value in self.names and self.names[value] != self._glyph.name:
                raise ValueError(
                    error.generateErrorMessage(
                        "duplicateAttributeValue",
                        value=value,
                        attribute="smufl.name",
                        objectName="Glyph",
                        conflictingInstance=self.names[value],
                    )
                )

            if self._glyph.name in self.names.values():
                self.names = {
                    k: v for k, v in self.names.items() if v != self._glyph.name
                }

            self.names[value] = self._glyph.name

    def _updateNames(self, value: str | None) -> None:
        # Keep dynamic dict of glyph names in font.lib.
        if value is None:
            self._clearNames()
        else:
            self._addNames(value)

    # ----------
    # Predicates
    # ----------

    @property
    def isLigature(self) -> bool:
        """Return :obj:`True` if glyph is ligature.

        This property is read-only.

        Example::

            >>> glyph = font["uniE09E_uniE083_uniE09F_uniE084"]
            >>> g1.smufl.isLigature
            True
            >>> glyph = font["uniE083"]
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
        """Return :obj:`True` if glyph is either `recommended or optional
        <https://w3c.github.io/smufl/latest/about/recommended-chars-\
        optional-glyphs.html>`_.

        This property is read-only.

        Example::

            >>> glyph = font["uniE050"]
            >>> glyph.smufl.isMember
            True
            >>> glyph = font["spaces"]
            >>> glyph.smufl.isMember
            False

        """
        glyph = self._requireGlyphAccess("isMember")
        if glyph is not None and glyph.unicode and 0xE000 <= glyph.unicode <= 0xF8FF:
            return True
        return False

    @property
    def isOptional(self) -> bool:
        """Return :obj:`True` if glyph is `optional <https://w3c.github.io\
        /smufl/latest/about/recommended-chars-optional-glyphs.html>`_.

        This property is read-only.

        Example::

            >>> glyph = font["uniF660"]
            >>> g1.smufl.isOptional
            True
            >>> glyph = font["uniE083"]
            >>> glyph.smufl.isOptional
            False

        """
        glyph = self._requireGlyphAccess("isOptional")
        if glyph is not None and glyph.unicode and 0xF400 <= glyph.unicode <= 0xF8FF:
            return True
        return False

    @property
    def isRecommended(self) -> bool:
        """Return :obj:`True` if glyph is `recommended <https://w3c.github.io\
        /smufl/latest/about/recommended-chars-optional-glyphs.html>`_.

        This property is read-only.

        Example::

            >>> glyph = font["uniE083"]
            >>> g1.smufl.isRecommended
            True
            >>> glyph = font["uniF660"]
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

        Example::

            >>> glyph = font["uniE042.salt01"]
            >>> glyph.smufl.isSalt
            True
            >>> glyph = font["uniE042"]
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

        Example::

            >>> glyph = font["uniE050.ss01"]
            >>> glyph.smufl.isSet
            True
            >>> glyph = font["uniE042.salt01"]
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

        Examples::

            >>> glyph.smufl.advanceWidth
            230.5
            >>> glyph.smufl.round()
            >>> glyph.smufl.advanceWidthdth
            231

        ::

            >>> glyph.smufl.spaces = True
            >>> glyph.smufl.advanceWidth
            0.922
            >>> glyph.smufl.round()
            >>> glyph.smufl.advanceWidth
            0.922

        """
        if self.spaces:
            return

        if self.engravingDefaults:
            self.engravingDefaults.round()

        if self._glyph is not None:
            self._glyph.round()

    def toSpaces(self, value: int | float) -> float | None:
        """Convert font units to staff spaces based on font UPM size.

        The inverse of :meth:`toUnits`.

        :param value: Value to convert.

        Example::

            >>> f = Font("path/to/my/font.ufo")
            >>> font.info.unitsPerEm
            2048
            >>> font.smufl.toSpaces(512)
            1.0

        """
        if self.font is None:
            return None

        if not self.font.info.unitsPerEm:
            raise AttributeError(
                error.generateErrorMessage(
                    "missingDependencyError",
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

        The inverse of :meth:`toSpaces`.
        Result is always rounded.

        :param value: Value to convert.
        :param rounded: Whether to round result to nearest integer.

        Example::

            >>> f = Font("path/to/my/font.ufo")
            >>> font.info.unitsPerEm
            2048
            >>> font.smufl.toSpaces(2)
            1024

        """
        if self.font is None:
            return None

        if not self.font.info.unitsPerEm:
            raise AttributeError(
                error.generateErrorMessage(
                    "missingDependencyError",
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

        Example::

            >>> glyph.smufl.advanceWidth
            230.5
            >>> glyph.smufl.spaces = True
            >>> glyph.smufl.advanceWidth
            0.922

        """
        if self.font is None:
            return False
        return self.font.lib.naked().get("com.smufolib.spaces", False)

    @spaces.setter
    def spaces(self, value):
        if self.font is not None:
            if not self.font.info.unitsPerEm:
                raise AttributeError(
                    error.generateErrorMessage(
                        "missingDependencyError",
                        objectName="spaces",
                        dependency="font.info.unitsPerEm",
                    )
                )
            value = normalizers.normalizeBoolean(value)
            if value:
                self.font.lib.naked()["com.smufolib.spaces"] = True
            else:
                self.font.lib.naked().pop("com.smufolib.spaces", False)

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
