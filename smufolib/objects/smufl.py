# pylint: disable=C0103, C0114, R0904, W0212, W0221
from __future__ import annotations
from typing import TYPE_CHECKING, Any
import re

from fontParts.base.base import BaseObject
from smufolib.objects.range import Range
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

    This class may be called from either :class:`.Font`
    or :class:`.Glyph`. Font-specific attributes with unique names may
    be accessed from both, due to the consistent access to parent
    classes in FontParts.

    .. _about glyph naming:
    .. note:: Attributes with the purpose of identifying ligatures
       (:attr:`isLigature`), stylistic alternates (:attr:`isSalt`) and
       stylistic sets (:attr:`isSet`) depend on strict adherence to the
       descriptive naming schemes stipulated in the `Adobe Glyph List\
       Specification <https://github.com/adobe-type-tools/agl-\
       specification#readme>`_ and followed by the SMuFL standard
       (see `Section 6 <https://github.com/adobe-type-tools/agl-\
       specification#6-assigning-glyph-names-in-new-fonts>`_ for more
       information).

    .. tip:: To avoid having to set all the glyph identification
       attributes manually, it is advisable to run the
       script :mod:`.importID` prior to using this class with an
       excisting font for the first time.

    :param font: Parent :class:`.Font` object.
    :param glyph: Parent :class:`.Glyph` object.

    While this object is normally created as part of a :class:`.Font`,
    an orphan :class:`Smufl` object can be created like this::

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
            contents += self.glyph._reprContents()  # type: ignore
        if self.font is not None:
            contents.append("in font")
            contents += self.font._reprContents()
        return contents

    def naked(self):
        # BaseObject override for __eq__ and __hash__
        return self

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
        return self.font.lib.get("com.smufolib.designSize", None)

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
            <EngravingDefaults at 4540156752>

        """
        return EngravingDefaults(self)

    @engravingDefaults.setter
    def engravingDefaults(self, value: EngravingDefaults) -> None:
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
        return self.font.lib.get("com.smufolib.sizeRange", None)

    @sizeRange.setter
    def sizeRange(self, value: tuple[int, int] | None) -> None:
        self._updateFontLib(
            "com.smufolib.sizeRange", normalizers.normalizeSizeRange(value)
        )

    def _updateFontLib(self, key: str, value: Any) -> None:
        # Common font metadata setter.
        if self.font is not None:
            if value is None:
                self.font.lib.pop(key, None)
            else:
                self.font.lib[key] = value

    # --------------
    # Glyph metadata
    # --------------

    @property
    def alternates(self) -> tuple[dict[str, str], ...] | None:
        """Metadata of glyph alternates.

        This property is read-only.

        Example::

            >>> glyph = font['uniE050'] # gClef
            >>> glyph.smufl.alternates
            ({'codepoint': 'U+F472', 'name': 'gClefSmall'},)

        """
        if self.glyph is None or self.font is None:
            return None
        # find alt names among string of glyph names
        string = " ".join(sorted(self.font.keys()))
        pattern = rf"\b{self.glyph.name}\.(?:s?alt|ss)[0-9]{{2}}\b"
        results = re.findall(pattern, string)
        alternates = []
        for name in results:
            glyph = self.font[name]
            alternates.append(
                {"codepoint": glyph.smufl.codepoint, "name": glyph.smufl.name}
            )
        return tuple(alternates)

    @property
    def anchors(self) -> dict[str, tuple[int | float, int | float]] | None:
        """SMuFL-specific glyph anchors as Cartesian coordinates.

        This property is read-only. Use
        the :attr:`fontParts.base.BaseGlyph.anchors` attribute to set
        glyph anchors.

        Example::

            >>> glyph = font['uniE0A3'] # noteheadHalf
            >>> glyph.smufl.anchors
            {'cutOutNW': (0.204, 0.296), 'cutOutSE':
            (0.98, -0.3), 'splitStemDownNE': (0.956, -0.3), 'splitStemDownNW':
            (0.128, -0.428), 'splitStemUpSE': (1.108, 0.372), 'splitStemUpSW':
            (0.328, 0.38), 'stemDownNW': (0.0, -0.168), 'stemUpSE': (1.18, 0.168)}

        """
        if self.glyph is None:
            return None

        anchors = {}
        for a in self.glyph.naked().anchors:
            if a.name in ANCHOR_NAMES:
                x = self.toSpaces(a.x) if self.spaces else a.x
                y = self.toSpaces(a.y) if self.spaces else a.y

                if x is None or y is None:
                    return None

                anchors[a.name] = (x, y)

        return anchors

    @property
    def bBox(self) -> dict[str, tuple[int | float, int | float]] | None:
        """Glyph bounding box as Cartesian coordinates.

        This property is read-only.

        Example::

            >>> glyph.smufl.bBox
            {'bBoxSW': (0.0, -0.5), 'bBoxNE': (1.18, 0.5)}

        """
        if self.glyph is None or not self.glyph.bounds:
            return None
        xMin, yMin, xMax, yMax = self.glyph.bounds
        if self.spaces:
            xMin, yMin, xMax, yMax = [self.toSpaces(b) for b in self.glyph.bounds]
        return {"bBoxSW": (xMin, yMin), "bBoxNE": (xMax, yMax)}

    @property
    def codepoint(self) -> str | None:
        """Unicode codepoint as formatted string.

        Example::

            >>> glyph = font['uniE0A3']
            >>> glyph.smufl.codepoint
            U+E0A3

        """
        if self.glyph is None or not self.glyph.unicode:
            return None
        return converters.toUniHex(self.glyph.unicode)

    @codepoint.setter
    def codepoint(self, value: str | None) -> None:
        if self.glyph is not None:
            if value is None:
                self.glyph.unicode = None
            else:
                self.glyph.unicode = converters.toDecimal(value)

    @property
    def componentGlyphs(self) -> tuple[Glyph, ...] | None:
        """Ligature components by :class:`.Glyph` object.

        This property is read-only.

        Example::

            >>> glyph = font['uniE09E_uniE083_uniE09F_uniE084']
            >>> glyph.smufl.componentGlyphs
            (<Glyph 'uniE09E' ('public.default') at 4399803376>,
             <Glyph 'uniE083' ('public.default') at 4399803184>,
             <Glyph 'uniE09F' ('public.default') at 4399797952>,
             <Glyph 'uniE084' ('public.default') at 4399797760>)

        """
        if self.glyph is None or self.font is None:
            return None
        if not self.isLigature:
            return ()

        components = [
            self.font[n] for n in self.glyph.name.split("_") if n in self.font
        ]
        return tuple(components)

    @property
    def componentNames(self) -> tuple[str | None, ...] | None:
        """Ligature components by :attr:`name`.

        This property is read-only.

        Example::

            >>> glyph = font['uniE09E_uniE083_uniE09F_uniE084']
            >>> glyph.smufl.componentNames
            ('timeSigCombNumerator', 'timeSig3',
             'timeSigCombDenominator', 'timeSig4')

        """
        if self.glyph is None or self.font is None:
            return None
        if not self.componentGlyphs:
            return ()

        components = [g.smufl.name for g in self.componentGlyphs]
        return tuple(components)

    @property
    def range(self) -> Range:
        """Glyph's :class:`.Range` object.

        This property is read-only.

        Example::

            >>> glyph = font['uniE212'] # stemSwished
            >>> glyph.smufl.range
            <Range 'stems' ('U+E210–U+E21F') at 4348391632>

        """
        return Range(self)

    @property
    def advanceWidth(self) -> int | float | None:
        """Glyph advance width.

        This property is equivalent
        to :attr:`fontParts.base.BaseGlyph.width`.

        Example::

            >>> glyph.smufl.advanceWidth
            671

        """
        if self.glyph is None:
            return None
        if self.spaces:
            return self.toSpaces(self.glyph.width)
        return self.glyph.width

    @advanceWidth.setter
    def advanceWidth(self, value: int | float | None) -> None:
        if self.glyph is not None:
            if self.spaces and value is not None:
                self.glyph.width = self.toUnits(value)
            else:
                self.glyph.width = value

    # --------------
    # Identification
    # --------------

    # Font
    # ----

    # Font family name is acessible through font.smufl.name.

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

            >>> glyph = font['uniE354'] # accSagittalSharp7v11kUp
            >>> glyph.smufl.classes
            ['accidentals', 'accidentalsSagittalAthenian', 'combiningStaffPositions']

        """
        if self.glyph is None:
            return None
        return tuple(self.glyph.lib.get("com.smufolib.classes", ()))

    @classes.setter
    def classes(self, value: tuple[str, ...] | None) -> None:
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
        if self.glyph is None:
            return None
        return self.glyph.lib.get("com.smufolib.description", None)

    @description.setter
    def description(self, value: str | None) -> None:
        self._updateGlyphLib(
            "com.smufolib.description", normalizers.normalizeDescription(value)
        )

    @property
    def name(self) -> str | None:
        """SMuFL-specific canonical font or glyph name.

        Examples::

            >>> font.smufl.name
            Bravura

        ::

            >>> glyph = font['uniE212']
            >>> glyph.smufl.name
            stemSwished

        """
        if self.font is None:
            return None
        if self.glyph is None:
            return self.font.info.naked().familyName
        return self.glyph.lib.get("com.smufolib.name", None)

    @name.setter
    def name(self, value: str | None) -> None:
        # Update com.smufolib.names before ID property
        if self.font is None:
            return

        if self.glyph is None:
            self.font.info.naked().familyName = value
        else:
            self._updateNames(normalizers.normalizeSmuflName(value))
            self._updateGlyphLib(
                "com.smufolib.name", normalizers.normalizeSmuflName(value)
            )

    def _updateGlyphLib(self, key: str, value: Any) -> None:
        if self.glyph is not None:
            if not value:
                if key in self.glyph.lib:
                    del self.glyph.lib[key]
            else:
                self.glyph.lib[key] = value

    def _clearNames(self) -> None:
        if self.font is not None:
            if self._names:
                self.font.lib["com.smufolib.names"].pop(self.name)
            if not self._names:
                self.font.lib.pop("com.smufolib.names")

    def _addNames(self, value: Any) -> None:
        if self._names is None:
            self._names = {}
        if self.glyph is not None:
            self._names[value] = self.glyph.name

    def _updateNames(self, value: str | None) -> None:
        # Keep dynamic dict of glyph names in font.lib.
        if value is None:
            self._clearNames()
        else:
            self._addNames(value)

    @property
    def _names(self) -> dict[str, str] | None:
        # Dict of glyph names in font.lib.
        if self.font is None:
            return None
        return self.font.lib.get("com.smufolib.names")

    @_names.setter
    def _names(self, value: dict[str, str] | None) -> None:
        self._updateFontLib("com.smufolib.names", value)

    # ----------
    # Validation
    # ----------

    @property
    def isLigature(self) -> bool:
        """Return :obj:`True` if glyph is ligature.

        This property is read-only.

        Example::

            >>> glyph = font['uniE09E_uniE083_uniE09F_uniE084']
            >>> g1.smufl.isLigature
            True
            >>> glyph = font['uniE083']
            >>> glyph.smufl.isLigature
            False

        """
        if (
            self.glyph is not None
            and self.glyph.name
            and self.glyph.name.count("uni") > 1
            and "_" in self.glyph.name
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

            >>> glyph = font['uniE050']
            >>> glyph.smufl.isMember
            True
            >>> glyph = font['spaces']
            >>> glyph.smufl.isMember
            False

        """
        if (
            self.glyph is not None
            and self.glyph.unicode
            and 0xE000 <= self.glyph.unicode <= 0xF8FF
        ):
            return True
        return False

    @property
    def isOptional(self) -> bool:
        """Return :obj:`True` if glyph is `optional <https://w3c.github.io\
        /smufl/latest/about/recommended-chars-optional-glyphs.html>`_.

        This property is read-only.

        Example::

            >>> glyph = font['uniF660']
            >>> g1.smufl.isOptional
            True
            >>> glyph = font['uniE083']
            >>> glyph.smufl.isOptional
            False

        """
        if (
            self.glyph is not None
            and self.glyph.unicode
            and 0xF400 <= self.glyph.unicode <= 0xF8FF
        ):
            return True
        return False

    @property
    def isRecommended(self) -> bool:
        """Return :obj:`True` if glyph is `recommended <https://w3c.github.io\
        /smufl/latest/about/recommended-chars-optional-glyphs.html>`_.

        This property is read-only.

        Example::

            >>> glyph = font['uniE083']
            >>> g1.smufl.isRecommended
            True
            >>> glyph = font['uniF660']
            >>> glyph.smufl.isRecommended
            False

        """
        if (
            self.glyph is not None
            and self.glyph.unicode
            and 0xE000 <= self.glyph.unicode <= 0xF3FF
        ):
            return True
        return False

    @property
    def isSalt(self) -> bool:
        """Return :obj:`True` if glyph is stylistic alternate.

        Glyph names with either ``'.alt'`` and ``'.salt'`` suffix are
        accepted. See :ref:`Note <about glyph naming>` about glyph
        naming.

        This property is read-only.

        Example::

            >>> glyph = font['uniE042.salt01']
            >>> glyph.smufl.isSalt
            True
            >>> glyph = font['uniE042']
            >>> glyph.smufl.isSalt
            False

        """
        if (
            self.glyph is not None
            and self.glyph.name
            and (
                self.glyph.name.endswith(".salt", 7, -2)
                or self.glyph.name.endswith(".alt", 7, -2)
            )
        ):
            return True
        return False

    @property
    def isSet(self) -> bool:
        """Return :obj:`True` if glyph is stylistic set member.

        See :ref:`Note <about glyph naming>` about glyph naming.

        This property is read-only.

        Example::

            >>> glyph = font['uniE050.ss01']
            >>> glyph.smufl.isSet
            True
            >>> glyph = font['uniE042.salt01']
            >>> glyph.smufl.isSet
            False

        """
        if (
            self.glyph is not None
            and self.glyph.name
            and self.glyph.name.endswith(".ss", 7, -2)
        ):
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
        - :attr:`.BaseGlyph.width`
        - :attr:`.BaseGlyph.height`
        - :attr:`.BaseGlyph.contours`
        - :attr:`.BaseGlyph.components`
        - :attr:`.BaseGlyph.anchors`
        - :attr:`.BaseGlyph.guidelines`


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
        self.engravingDefaults.round()
        if self.glyph is not None:
            self.glyph.round()

    def toSpaces(self, value: int | float) -> float | None:
        """Convert font units to staff spaces based on font UPM size.

        The inverse of :meth:`toUnits`.

        :param value: Value to convert.

        Example::

            >>> f = Font('path/to/my/font.ufo')
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

            >>> f = Font('path/to/my/font.ufo')
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
        return self.font.lib.get("com.smufolib.spaces", False)

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
                self.font.lib["com.smufolib.spaces"] = True
            else:
                self.font.lib.pop("com.smufolib.spaces", False)

    # -----
    # Other
    # -----

    @property
    def base(self) -> Glyph | None:
        """:class:`.Glyph` object of alternate's base glyph.

        This property is read-only.

        Example::

            >>> glyph = font['uniE050.ss01']
            >>> glyph.smufl.base
            <Glyph 'uniE050' ('public.default') at 4373577008>

        """
        baseName = self._getBasename()
        if self.font and baseName:
            return self.font[baseName]
        return None

    def _getBasename(self) -> str | None:
        # Get name of base glyph.
        if self.glyph is None or self.glyph.name is None:
            return None
        basename = self.glyph.name[:7]
        return basename if self.font and basename in self.font else None

    def findGlyph(self, name: str) -> Glyph | None:
        """Find :class:`.Glyph` object from :attr:`name`.

        :param name: SMuFL-specific canonical glyph name.

        Example::

            >>> font.smufl.findGlyph('barlineSingle')
            <Glyph 'uniE030' ('public.default') at 4393557200>

        """
        if name is None:
            return None

        normalizedName = normalizers.normalizeSmuflName(name)

        if (
            self.font is None
            or self._names is None
            or normalizedName not in self._names
        ):
            return None

        return self.font[self._names[normalizedName]]

    @property
    def suffix(self) -> str | None:
        """Return suffix of alternates.

        This property is read-only.

        Example::

            >>> glyph = font['uniE050.ss01']
            >>> glyph.smufl.suffix
            ss01

        """
        if self.glyph is not None and (self.isSalt or self.isSet):
            return self.glyph.name.split(".")[1]
        return None

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
