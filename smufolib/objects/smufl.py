# pylint: disable=C0114, R0904, C0103, W0212
from __future__ import annotations
from typing import TYPE_CHECKING
import re

from fontParts.base.base import BaseObject

from smufolib.objects.range import Range
from smufolib.objects.engravingDefaults import EngravingDefaults
from smufolib import converters, normalizers
from smufolib.constants import ANCHOR_NAMES

if TYPE_CHECKING:
    from smufolib.objects.layer import Layer
    from smufolib.objects.font import Font
    from smufolib.objects.glyph import Glyph


class Smufl(BaseObject):
    """Provides SMuFL-related metadata and functionality.

    Class may be called from either :class:`~smufolib.objects.font.Font`
    or :class:`~smufolib.objects.glyph.Glyph`. Font-specific attributes
    with unique names may be accessed from both, due to the consistent
    access to parent classes in FontParts.

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
       script :mod:`~bin.importID` prior to using this class with
       an excisting font for the first time.

    :param font: Parent :class:`~smufolib.objects.font.Font` object.
    :param glyph: Parent :class:`~smufolib.objects.glyph.Glyph` object.

    While this object is normally created as part of
    a :class:`~smufolib.objects.font.Font`, an orphan :class:`Smufl`
    object can be created like this::

        >>> smufl = Smufl()

    """

    def __init__(self,
                 font: Font | None = None,
                 glyph: Glyph | None = None) -> None:
        self._font = font
        self._glyph = glyph
        self._layer = None

    def _reprContents(self) -> list[str]:
        contents = []
        if self.glyph is not None:
            contents.append("in glyph")
            contents += self.glyph._reprContents()
        if self.font:
            contents.append("in font")
            contents += self.font._reprContents()
        return contents

    # -------
    # Parents
    # -------

    @property
    def font(self) -> Font | None:
        """Parent :class:`~smufolib.objects.font.Font` object.

        Example::

            >>> glyph.smufl.font
            <Font 'MyFont' path='path/to/my/font.ufo' at 4405856720>

        """
        if self._font is not None:
            return normalizers.normalizeFont(self._font)
        if self._glyph is not None:
            return self._glyph.font
        return None

    @font.setter
    def font(self, value: Font) -> None:
        if self._font is not None and self._font != value:
            raise AssertionError("Font for Smufl object is already "
                                 "set and is not same as value.")
        if self._glyph is not None:
            raise AssertionError("Glyph for Smufl object is already set.")
        self._font = normalizers.normalizeFont(value)

    @property
    def glyph(self) -> Glyph | None:
        """Parent :class:`~smufolib.objects.glyph.Glyph` object.

        Example::

            >>> glyph.smufl.glyph
            <Glyph 'uniE587' ('public.default') at 4536458160>

        """
        if self._glyph is None:
            return None
        return normalizers.normalizeGlyph(self._glyph)

    @glyph.setter
    def glyph(self, value: Glyph) -> None:
        if self._font is not None:
            raise AssertionError("Font for Smufl object is already set.")
        if self._glyph is not None and self._glyph != value:
            raise AssertionError("Glyph for Smufl object is already "
                                 "set and is not same as value.")
        self._glyph = normalizers.normalizeGlyph(value)

    @property
    def layer(self) -> Layer | None:
        """Parent :class:`~smufolib.objects.layer.Layer` object.

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
        return self.font.lib.get('_designSize', None)

    @designSize.setter
    def designSize(self, value: int) -> None:
        if value is None:
            self.font.lib.naked().pop('_designSize', None)
        else:
            value = normalizers.normalizeDesignSize(value)
            self.font.lib['_designSize'] = value

    @property
    def engravingDefaults(self) -> EngravingDefaults:
        """Font's :class:`~smufolib.objects.engravingDefaults.EngravingDefaults` object.

        Example::

            >>> font.smufl.engravingDefaults
            <EngravingDefaults at 4540156752>

        """
        return EngravingDefaults(self)

    @property
    def sizeRange(self) -> tuple[int, int] | None:
        """Optimum size range in integral decipoints.

        Example::

            >>> font.smufl.designSize
            (180, 260)

        """
        if self.font is None:
            return None
        return self.font.lib.naked().get('_sizeRange', ())

    @sizeRange.setter
    def sizeRange(self, value: tuple[int, int] | None) -> None:
        if value is None:
            self.font.lib.pop('_sizeRange', None)
        else:
            self.font.lib['_sizeRange'] = normalizers.normalizeSizeRange(value)

    # --------------
    # Glyph metadata
    # --------------

    @property
    def alternates(self) -> tuple[dict[str, str], ...] | None:
        """Metadata of glyph alternates.

        Example::

            >>> glyph = font['uniE050'] # gClef
            >>> glyph.smufl.alternates
            ({'codepoint': 'U+F472', 'name': 'gClefSmall'},)

        """
        if self._glyph is None:
            return None
        # find alt names among string of glyph names
        string = ' '.join(sorted(self.font.keys()))
        pattern = fr'\b{self.glyph.name}\.(?:s?alt|ss)[0-9]{{2}}\b'
        results = re.findall(pattern, string)
        alternates = []
        for name in results:
            glyph = self.font[name]
            alternates.append({'codepoint': glyph.smufl.codepoint,
                               'name': glyph.smufl.name})
        return tuple(alternates)

    @property
    def anchors(self) -> dict[str, tuple[int | float, int | float]] | None:
        """SMuFL-specific glyph anchors as Cartesian coordinates.

        Example::

            >>> glyph = font['uniE0A3'] # noteheadHalf
            >>> glyph.smufl.anchors
            {'cutOutNW': (0.204, 0.296), 'cutOutSE':
            (0.98, -0.3), 'splitStemDownNE': (0.956, -0.3), 'splitStemDownNW':
            (0.128, -0.428), 'splitStemUpSE': (1.108, 0.372), 'splitStemUpSW':
            (0.328, 0.38), 'stemDownNW': (0.0, -0.168), 'stemUpSE': (1.18, 0.168)}

        """

        if self._glyph is None:
            return None
        if self.spaces:
            return {a.name: (self.toSpaces(a.x), self.toSpaces(a.y)) for a in
                    self.glyph.naked().anchors if a.name in ANCHOR_NAMES}
        return {a.name: (a.x, a.y) for a in
                self.glyph.naked().anchors if a.name in ANCHOR_NAMES}

    @property
    def bBox(self) -> dict[str, tuple[int | float, int | float]] | None:
        """Glyph bounding box as Cartesian coordinates.

        Example::

            >>> glyph.smufl.bBox
            {'bBoxSW': (0.0, -0.5), 'bBoxNE': (1.18, 0.5)}

        """
        if self._glyph is None or not self.glyph.bounds:
            return None
        xMin, yMin, xMax, yMax = self.glyph.bounds
        if self.spaces:
            xMin, yMin, xMax, yMax = [
                self.toSpaces(b) for b in self.glyph.bounds]
        return {"bBoxSW": (xMin, yMin), "bBoxNE": (xMax, yMax)}

    @property
    def codepoint(self) -> str | None:
        """Unicode codepoint as formatted string.

        Example::

            >>> glyph = font['uniE0A3']
            >>> glyph.smufl.codepoint
            U+E0A3

        """
        if self._glyph is None or not self.glyph.unicode:
            return None
        return converters.toUniHex(self.glyph.unicode)

    @property
    def componentGlyphs(self) -> tuple[str, ...] | None:
        """Ligature components by :attr:`name`.

        Example::

            >>> glyph = font['uniE09E_uniE083_uniE09F_uniE084']
            >>> glyph.smufl.componentGlyphs
            ('timeSigCombNumerator', 'timeSig3', 'timeSigCombDenominator', 'timeSig4')

        """
        if self._glyph is None:
            return None
        if self.glyph.name is None or '_' not in self.glyph.name:
            return ()
        names = self.glyph.name.split('_')
        components = []
        for name in names:
            if name not in self.font:
                continue
            glyph = self.font[name]
            if not self.name:
                continue
            components.append(glyph.smufl.name)
        return tuple(components)

    @property
    def range(self) -> Range:
        """Glyph's :class:`~smufolib.objects.range.Range` object.

        Example::

            >>> glyph = font['uniE212'] # stemSwished
            >>> glyph.smufl.range
            <Range 'stems' ('U+E210–U+E21F') at 4348391632>

        """
        return Range(self)

    @property
    def advanceWidth(self) -> int | float | None:
        """Glyph advance width.

        Example::

            >>> glyph.smufl.advanceWidth
            671

        """
        if self._glyph is None:
            return None
        if self.spaces:
            return self.toSpaces(self.glyph.width)
        return self.glyph.width

    @advanceWidth.setter
    def advanceWidth(self, value: int | float | None) -> None:
        if self.spaces:
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
        return float(f'{self.font.info.naked().versionMajor}.'
                     f'{self.font.info.naked().versionMinor}')

    @version.setter
    def version(self, value: float | None) -> None:
        if value is None:
            major, minor = None, None
        else:
            major, minor = [int(n) for n in str(value).split('.')]
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
        if self._glyph is None:
            return None
        return tuple(self.glyph.lib.naked().get('_classes', ()))

    @classes.setter
    def classes(self, value: tuple[str, ...] | list[str] | None) -> None:
        self._set_id('_classes', normalizers.normalizeClasses(value))

    @property
    def description(self) -> str | None:
        """SMuFL-specific glyph description of optional glyphs.

        Example::

            >>> glyph.smufl.description
            Combining swished stem

        """
        if self._glyph is None:
            return None
        return self.glyph.lib.naked().get('_description', None)

    @description.setter
    def description(self, value: str | None) -> None:
        self._set_id('_description', normalizers.normalizeDescription(value))

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
        if self._glyph is None:
            if self._font is None:
                return None
            return self.font.info.naked().familyName
        return self.glyph.lib.naked().get('_name', None)

    @name.setter
    def name(self, value: str | None) -> None:
        # Update _names before ID property
        if self._glyph is None:
            self.font.info.naked().familyName = value
        else:
            self._updateNames(normalizers.normalizeSmuflName(value))
            self._set_id('_name', normalizers.normalizeSmuflName(value))

    def _set_id(self, attribute: str, value: str | list | None) -> None:
        # Common ID property setter.
        if self._glyph is None or self._names is None:
            return
        if value is None:
            if attribute not in self.glyph.lib.naked():
                return
            # naked() does not work here.
            self.glyph.lib.pop(attribute, None)
        else:
            self.glyph.lib[attribute] = value

    def _updateNames(self, value) -> None:
        # Keep dynamic dict of names in font.lib.
        if value is None:
            if self._names is None:
                return
            if (len(self._names) == 0 or len(self._names) == 1
                    and self.name in self._names):
                self._names = None
            else:
                self.font.lib.naked()['_names'].pop(self.name, None)
        else:
            if self._names is None:
                self._names = {}
            self._names[value] = self.glyph.name

    @property
    def _names(self) -> dict[str, str] | None:
        # Parent dict in font.lib.naked().
        if self.font is None:
            return None
        return self.font.lib.naked().get('_names')

    @_names.setter
    def _names(self, value: dict[str, str] | None) -> None:
        if value is None:
            self.font.lib.naked().pop('_names', None)
        else:
            self.font.lib.naked()['_names'] = value

    # ----------
    # Validation
    # ----------

    @property
    def isLigature(self) -> bool:
        """Return :obj:`True` if glyph is ligature.

        Example::

            >>> glyph = font['uniE09E_uniE083_uniE09F_uniE084']
            >>> g1.smufl.isLigature
            True
            >>> glyph = font['uniE083']
            >>> glyph.smufl.isLigature
            False

        """
        if (self._glyph is not None and self.glyph.name
            and self.glyph.name.count('uni') > 1
                and '_' in self.glyph.name):
            return True
        return False

    @property
    def isMember(self) -> bool:
        """Return :obj:`True` if glyph is either `recommended or optional
        <https://w3c.github.io/smufl/latest/about/recommended-chars-\
        optional-glyphs.html>`_.

        Example::

            >>> glyph = font['uniE050']
            >>> glyph.smufl.isMember
            True
            >>> glyph = font['spaces']
            >>> glyph.smufl.isMember
            False

        """
        if (self._glyph is not None and self.glyph.unicode
                and 0xe000 <= self.glyph.unicode <= 0xf8ff):
            return True
        return False

    @property
    def isOptional(self) -> bool:
        """Return :obj:`True` if glyph is `optional <https://w3c.github.io\
        /smufl/latest/about/recommended-chars-optional-glyphs.html>`_.

        Example::

            >>> glyph = font['uniF660']
            >>> g1.smufl.isOptional
            True
            >>> glyph = font['uniE083']
            >>> glyph.smufl.isOptional
            False

        """
        if (self._glyph is not None and self.glyph.unicode
                and 0xF400 <= self.glyph.unicode <= 0xF8FF):
            return True
        return False

    @property
    def isRecommended(self) -> bool:
        """Return :obj:`True` if glyph is `recommended <https://w3c.github.io\
        /smufl/latest/about/recommended-chars-optional-glyphs.html>`_.

        Example::

            >>> glyph = font['uniE083']
            >>> g1.smufl.isRecommended
            True
            >>> glyph = font['uniF660']
            >>> glyph.smufl.isRecommended
            False

        """
        if (self._glyph is not None and self.glyph.unicode
                and 0xE000 <= self.glyph.unicode <= 0xF3FF):
            return True
        return False

    @property
    def isSalt(self) -> bool:
        """Return :obj:`True` if glyph is stylistic alternate.

        Accepts both ``'.alt'`` and ``'.salt'`` suffix.
        See :ref:`Note <about glyph naming>` about glyph naming.

        Example::

            >>> glyph = font['uniE042.salt01']
            >>> glyph.smufl.isSalt
            True
            >>> glyph = font['uniE042']
            >>> glyph.smufl.isSalt
            False

        """
        if (self._glyph is not None and self.glyph.name
                and (self.glyph.name.endswith('.salt', 7, -2)
                     or self.glyph.name.endswith('.alt', 7, -2))):
            return True
        return False

    @property
    def isSet(self) -> bool:
        """Return :obj:`True` if glyph is stylistic set member.

        See :ref:`Note <about glyph naming>` about glyph naming.

        Example::

            >>> glyph = font['uniE050.ss01']
            >>> glyph.smufl.isSet
            True
            >>> glyph = font['uniE042.salt01']
            >>> glyph.smufl.isSet
            False

        """
        if (self._glyph is not None and self.glyph.name
                and self.glyph.name.endswith('.ss', 7, -2)):
            return True
        return False

    # -----------------------------
    # Normalization and Measurement
    # -----------------------------

    def round(self) -> None:
        """Round font units to integers.

        Method applies to the following attributes:

        * :attr:`engravingDefaults`
        * :attr:`anchors`
        * :attr:`advanceWidth`

        If :attr:`spaces` is ``True``, values are left unchanged.

        Examples::

            >>> glyph.smufl.advanceWidth
            230.5
            >>> glyph.smufl.round()
            >>> glyph.smufl.wiadvanceWidthdth
            230.5

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
        if self._glyph is None:
            self.font.round()
        else:
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

        return converters.convertMeasurement(
            value,
            convertTo='spaces',
            unitsPerEm=self.font.info.unitsPerEm,
            rounded=False)

    def toUnits(self, value: int | float) -> int | None:
        """Convert staff spaces to font units based on font UPM size.

        The inverse of :meth:`toSpaces`.
        Result is always rounded.

        :param value: Value to convert.

        Example::

            >>> f = Font('path/to/my/font.ufo')
            >>> font.info.unitsPerEm
            2048
            >>> font.smufl.toSpaces(2)
            1024

        """
        if self.font is None:
            return None
        return converters.convertMeasurement(
            value,
            convertTo='units',
            unitsPerEm=self.font.info.unitsPerEm,
            rounded=True)

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
        if '_spaces' in self.font.lib.naked():
            return True
        return False

    @spaces.setter
    def spaces(self, value):
        value = normalizers.normalizeBoolean(value)
        if value is False:
            self.font.lib.naked().pop('_spaces', None)
        else:
            self.font.lib.naked()['_spaces'] = True

    # -----
    # Other
    # -----

    @property
    def base(self) -> Glyph | None:
        """:class:`~smufolib.objects.glyph.Glyph` object of alternate's base glyph.

        Example::

            >>> glyph = font['uniE050.ss01']
            >>> glyph.smufl.base
            <Glyph 'uniE050' ('public.default') at 4373577008>

        """
        if self._getBasename():
            return self.font[self._getBasename()]
        return None

    def _getBasename(self) -> str | None:
        # Get name of base glyph.
        if self._glyph is None or self.glyph.name is None:
            return None
        basename = self.glyph.name[:7]
        return basename if basename in self.font else None

    def findGlyph(self, name: str) -> Glyph | None:
        """Find :class:`~smufolib.objects.glyph.Glyph` object from :attr:`name`.

        :param name: SMuFL-specific canonical glyph name.

        Example::

            >>> font.smufl.findGlyph('barlineSingle')
            <Glyph 'uniE030' ('public.default') at 4393557200>

        """
        name = normalizers.normalizeSmuflName(name)
        if self._names is None or name not in self._names:
            return None
        return self.font[self._names[name]]

    @property
    def suffix(self) -> str | None:
        """Return suffix of alternates.

        Example::

            >>> glyph = font['uniE050.ss01']
            >>> glyph.smufl.suffix
            ss01

        """
        if not (self.isSalt or self.isSet):
            return None
        return self.glyph.name.split('.')[1]
