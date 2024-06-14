from __future__ import annotations
from typing import TYPE_CHECKING

from fontParts.base.base import BaseObject

from smufolib import normalizers
from smufolib.constants import ENGRAVING_DEFAULT_KEYS

if TYPE_CHECKING:
    from smufolib.objects.smufl import Smufl
    from smufolib.objects.glyph import Glyph
    from smufolib.objects.font import Font
    from smufolib.objects.layer import Layer

# pylint: disable=invalid-name, too-many-public-methods


class EngravingDefaults(BaseObject):
    """SMuFL engraving default settings.

    This object contains properties and methods pertained to SMuFL's
    `engravingDefaults
    <https://w3c.github.io/smufl/latest/specification/engravingdefaults.html>`_
    metadata structure, defining recommended defaults for line widths
    etc., according to the specification.

    The :class:`EngravingDefaults` object is essentially a :class:`dict`
    with access to keys through regular class attributes.

    .. tip:: Engraving default values can be calculated from the
       contours of specific glyphs and set automatically with
       the :mod:`~bin.calculateEngravingDefaults` script.

    :param smufl: Parent :class:`~smufolib.objects.smufl.Smufl` object.

    While this object is normally created as part of
    a :class:`~smufolib.objects.font.Font`, an
    orphan :class:`EngravingDefaults` object may be created like
    this::

        >>> d = EngravingDefaults()

    """

    def __init__(self, smufl: Smufl | None = None) -> None:
        self._smufl = smufl

    def _reprContents(self) -> list[str]:
        contents = []
        contents.append("in font")
        contents += self.font._reprContents()
        return contents

    # ------------------
    # Dictionary methods
    # ------------------

    def clear(self) -> None:
        """Clear all engraving default settings.

        Example::

            >>> d.items()
            {'arrowShaftThickness': 46, 'barlineSeparation': 72, ...}
            >>> d.clear()
            >>> d.items()
            {'arrowShaftThickness': None, 'barlineSeparation': None, ...}

        """
        self._engravingDefaults = None

    def items(self) -> dict[str, int | float | tuple[str, ...] | None]:
        """Return dict of all available settings and their values.

        Example::

            >>> d = f.smufl.engravingDefaults
            >>> d.items()
            {'arrowShaftThickness': 46, 'barlineSeparation': 72, ...}

        """
        return dict(zip(self.keys(), self.values()))

    def keys(self) -> list[str]:
        """Return sorted list of all available settings names.

        Example::

            >>> d = f.smufl.engravingDefaults
            >>> d.keys()
            ['arrowShaftThickness', 'barlineSeparation', ...]

        """
        return sorted(ENGRAVING_DEFAULT_KEYS)

    def update(self, other: EngravingDefaults
               | dict[str, int | float | tuple[str, ...] | None] = None,
               **kwargs: int | float | tuple[str, ...] | None) -> None:
        r"""Update settings attributes with other object or values.

        :param other: Other :class:`EngravingDefaults` or :class:`dict`
            of attribute names mapped to values.
        :param \**kwargs: Optional attribute names and values as keyword
            arguments.

        An object may be updated in a few different ways::

            >>> d1 = f.smufl.engravingDefaults
            >>> d1.items()
            {'arrowShaftThickness': None, 'barlineSeparation': None, ...}

        Update with :class:`dict` object.::

            >>> d2 = {'arrowShaftThickness': 46, 'barlineSeparation': 72, ...}
            >>> d1.update(d2)
            >>> d1.items()
            {'arrowShaftThickness': 46, 'barlineSeparation': 72, ...}

        Update with other :class:`EngravingDefaults` object.::

            >>> d2 = f2.smufl.engravingDefaults
            >>> d2.items()
            {'arrowShaftThickness': 46, 'barlineSeparation': 72, ...}
            >>> d1.update(d2)
            >>> d1.items()
            {'arrowShaftThickness': 46, 'barlineSeparation': 72, ...}

        Update with keyword arguments::

            >>> d1.update(arrowShaftThickness=46, barlineSeparation=72)
            >>> d1.items()
            {'arrowShaftThickness': 46, 'barlineSeparation': 72, ...}

        """
        other = self._normalizeOthers(other, kwargs)
        for key, value in other.items():
            if key not in self.keys():
                raise AttributeError(
                    f"'{type(self).__name__}' object has no attribute '{key}'")
            value = normalizers.normalizeEngravingDefaultsAttr(key, value)
            if key == 'textFontFamily' or not self.spaces:
                setattr(self, key, value)
            else:
                setattr(self, key, self.font.smufl.toUnits(value))

    def _normalizeOthers(self, other: EngravingDefaults
                         | dict[str, int | float | tuple[str, ...] | None],
                         kwargs: dict[str, int | float | tuple[str, ...]]
                         ) -> None:
        # Normalize update(other)
        if isinstance(other, EngravingDefaults):
            other = other.items()
        if other is None:
            other = {}
            if not kwargs:
                raise TypeError(f"{type(self).__name__}.update() is missing 1 "
                                "required positional argument: 'other'.")
        elif not isinstance(other, dict):
            raise TypeError(
                "Expected EngravingDefaults object, dict or keyword "
                f"arguments, not '{type(other).__name__}'.")
        other |= kwargs
        return other

    def values(self) -> list[str]:
        """Return list of all available settings values.

        Order corresponds to :meth:`keys`.

        Example::

            >>> d = f.smufl.engravingDefaults
            >>> d.values()
            [46, 72, 62, 125, 125, 125, 57, 36, 200, 39, 80, 40, ...]

        """
        return [getattr(self, k) for k in self.keys()]

    # -------
    # Parents
    # -------

    @property
    def smufl(self) -> Smufl | None:
        """Parent :class:`~smufolib.objects.smufl.Smufl`."""
        if self._smufl is None and self.font is None:
            return None
        return normalizers.normalizeSmufl(self._smufl)

    @smufl.setter
    def smufl(self, value: Smufl) -> None:
        if self._smufl is not None and self._smufl != value:
            raise AssertionError("Smufl for EngravingDefaults object is "
                                 "already set and is not same as value.")
        self.font = normalizers.normalizeSmufl(value)

    @property
    def font(self) -> Font | None:
        """Parent :class:`~smufolib.objects.font.Font` object."""
        if self._smufl is None:
            return None
        return self._smufl.font

    @font.setter
    def font(self, value: Font) -> None:
        if self.smufl._font is not None and self.smufl._font != value:
            raise AssertionError("Font for EngravingDefaults object is "
                                 "already set and is not same as value.")
        self.font = normalizers.normalizeFont(value)

    @property
    def glyph(self) -> Glyph | None:
        """Parent :class:`~smufolib.objects.glyph.Glyph` object."""
        if self._smufl is None:
            return None
        return self._smufl.glyph

    @property
    def layer(self) -> Layer | None:
        """Parent :class:`~smufolib.objects.layer.Layer` object."""
        if self._smufl is None:
            return None
        return self._smufl.layer

    # -------------------
    # Settings Properties
    # -------------------

    @property
    def arrowShaftThickness(self) -> int | float | None:
        """Thickness of the line used for the shaft of an arrow."""
        return self._getValue('arrowShaftThickness')

    @arrowShaftThickness.setter
    def arrowShaftThickness(self, value: int | float | None) -> None:
        self._setValue('arrowShaftThickness', value)

    @property
    def barlineSeparation(self) -> int | float | None:
        """Distance between multiple thin barlines."""
        return self._getValue('barlineSeparation')

    @barlineSeparation.setter
    def barlineSeparation(self, value: int | float | None) -> None:
        self._setValue('barlineSeparation', value)

    @property
    def beamSpacing(self) -> int | float | None:
        """Distance between beams."""
        return self._getValue('beamSpacing')

    @beamSpacing.setter
    def beamSpacing(self, value: int | float | None) -> None:
        self._setValue('beamSpacing', value)

    @property
    def beamThickness(self) -> int | float | None:
        """Thickness of a beam."""
        return self._getValue('beamThickness')

    @beamThickness.setter
    def beamThickness(self, value: int | float | None) -> None:
        self._setValue('beamThickness', value)

    @property
    def bracketThickness(self) -> int | float | None:
        """Thickness of the vertical line of a grouping bracket."""
        return self._getValue('bracketThickness')

    @bracketThickness.setter
    def bracketThickness(self, value: int | float | None) -> None:
        self._setValue('bracketThickness', value)

    @property
    def dashedBarlineDashLength(self) -> int | float | None:
        """Length of the dashes to be used in a dashed barline."""
        return self._getValue('dashedBarlineDashLength')

    @dashedBarlineDashLength.setter
    def dashedBarlineDashLength(self, value: int | float | None) -> None:
        self._setValue('dashedBarlineDashLength', value)

    @property
    def dashedBarlineGapLength(self) -> int | float | None:
        """Length of the gap between dashes in a dashed barline."""
        return self._getValue('dashedBarlineGapLength')

    @dashedBarlineGapLength.setter
    def dashedBarlineGapLength(self, value: int | float | None) -> None:
        self._setValue('dashedBarlineGapLength', value)

    @property
    def dashedBarlineThickness(self) -> int | float | None:
        """Thickness of a dashed barline."""
        return self._getValue('dashedBarlineThickness')

    @dashedBarlineThickness.setter
    def dashedBarlineThickness(self, value: int | float | None) -> None:
        self._setValue('dashedBarlineThickness', value)

    @property
    def hairpinThickness(self) -> int | float | None:
        """Thickness of a crescendo/diminuendo hairpin."""
        return self._getValue('hairpinThickness')

    @hairpinThickness.setter
    def hairpinThickness(self, value: int | float | None) -> None:
        self._setValue('hairpinThickness', value)

    @property
    def hBarThickness(self) -> int | float | None:
        """Thickness of a crescendo/diminuendo hairpin."""
        return self._getValue('hBarThickness')

    @hBarThickness.setter
    def hBarThickness(self, value: int | float | None) -> None:
        self._setValue('hBarThickness', value)

    @property
    def legerLineExtension(self) -> int | float | None:
        """Amount of leger line extension from notehead."""
        return self._getValue('legerLineExtension')

    @legerLineExtension.setter
    def legerLineExtension(self, value: int | float | None) -> None:
        self._setValue('legerLineExtension', value)

    @property
    def legerLineThickness(self) -> int | float | None:
        """Thickness of a leger line."""
        return self._getValue('legerLineThickness')

    @legerLineThickness.setter
    def legerLineThickness(self, value: int | float | None) -> None:
        self._setValue('legerLineThickness', value)

    @property
    def lyricLineThickness(self) -> int | float | None:
        """Thickness of the lyric extension line."""
        return self._getValue('lyricLineThickness')

    @lyricLineThickness.setter
    def lyricLineThickness(self, value: int | float | None) -> None:
        self._setValue('lyricLineThickness', value)

    @property
    def octaveLineThickness(self) -> int | float | None:
        """Thickness of the dashed line used for an octave line."""
        return self._getValue('octaveLineThickness')

    @octaveLineThickness.setter
    def octaveLineThickness(self, value: int | float | None) -> None:
        self._setValue('octaveLineThickness', value)

    @property
    def pedalLineThickness(self) -> int | float | None:
        """Thickness of the line used for piano pedaling."""
        return self._getValue('pedalLineThickness')

    @pedalLineThickness.setter
    def pedalLineThickness(self, value: int | float | None) -> None:
        self._setValue('pedalLineThickness', value)

    @property
    def repeatBarlineDotSeparation(self) -> int | float | None:
        """Distance between dots and inner line of a repeat barline."""
        return self._getValue('repeatBarlineDotSeparation')

    @repeatBarlineDotSeparation.setter
    def repeatBarlineDotSeparation(self, value: int | float | None) -> None:
        self._setValue('repeatBarlineDotSeparation', value)

    @property
    def repeatEndingLineThickness(self) -> int | float | None:
        """Thickness of repeat ending brackets."""
        return self._getValue('repeatEndingLineThickness')

    @repeatEndingLineThickness.setter
    def repeatEndingLineThickness(self, value: int | float | None) -> None:
        self._setValue('repeatEndingLineThickness', value)

    @property
    def slurEndpointThickness(self) -> int | float | None:
        """Thickness of the end of a slur."""
        return self._getValue('slurEndpointThickness')

    @slurEndpointThickness.setter
    def slurEndpointThickness(self, value: int | float | None) -> None:
        self._setValue('slurEndpointThickness', value)

    @property
    def slurMidpointThickness(self) -> int | float | None:
        """Thickness of the mid-point of a slur."""
        return self._getValue('slurMidpointThickness')

    @slurMidpointThickness.setter
    def slurMidpointThickness(self, value: int | float | None) -> None:
        self._setValue('slurMidpointThickness', value)

    @property
    def staffLineThickness(self) -> int | float | None:
        """Thickness of each staff line."""
        return self._getValue('staffLineThickness')

    @staffLineThickness.setter
    def staffLineThickness(self, value: int | float | None) -> None:
        self._setValue('staffLineThickness', value)

    @property
    def stemThickness(self) -> int | float | None:
        """Thickness of a stem."""
        return self._getValue('stemThickness')

    @stemThickness.setter
    def stemThickness(self, value: int | float | None) -> None:
        self._setValue('stemThickness', value)

    @property
    def subBracketThickness(self) -> int | float | None:
        """Thickness of the vertical line of a grouping sub-bracket."""
        return self._getValue('subBracketThickness')

    @subBracketThickness.setter
    def subBracketThickness(self, value: int | float | None) -> None:
        self._setValue('subBracketThickness', value)

    @property
    def textFontFamily(self) -> tuple[str, ...]:
        """tuple of text font pairings."""
        return self._getValue('textFontFamily')

    @textFontFamily.setter
    def textFontFamily(self, value: tuple[str, ...]) -> None:
        self._setValue('textFontFamily', value)

    @property
    def textEnclosureThickness(self) -> int | float | None:
        """Thickness of box drawn around text instructions."""
        return self._getValue('textEnclosureThickness')

    @textEnclosureThickness.setter
    def textEnclosureThickness(self, value: int | float | None) -> None:
        self._setValue('textEnclosureThickness', value)

    @property
    def thickBarlineThickness(self) -> int | float | None:
        """Thickness of a thick barline."""
        return self._getValue('thickBarlineThickness')

    @thickBarlineThickness.setter
    def thickBarlineThickness(self, value: int | float | None) -> None:
        self._setValue('thickBarlineThickness', value)

    @property
    def thinBarlineThickness(self) -> int | float | None:
        """Thickness of a thin barline."""
        return self._getValue('thinBarlineThickness')

    @thinBarlineThickness.setter
    def thinBarlineThickness(self, value: int | float | None) -> None:
        self._setValue('thinBarlineThickness', value)

    @property
    def thinThickBarlineSeparation(self) -> int | float | None:
        """Thickness of a thin barline."""
        return self._getValue('thinThickBarlineSeparation')

    @thinThickBarlineSeparation.setter
    def thinThickBarlineSeparation(self, value: int | float | None) -> None:
        self._setValue('thinThickBarlineSeparation', value)

    @property
    def tieEndpointThickness(self) -> int | float | None:
        """Thickness of the end of a tie."""
        return self._getValue('tieEndpointThickness')

    @tieEndpointThickness.setter
    def tieEndpointThickness(self, value: int | float | None) -> None:
        self._setValue('tieEndpointThickness', value)

    @property
    def tieMidpointThickness(self) -> int | float | None:
        """Thickness of the mid-point of a tie."""
        return self._getValue('tieMidpointThickness')

    @tieMidpointThickness.setter
    def tieMidpointThickness(self, value: int | float | None) -> None:
        self._setValue('tieMidpointThickness', value)

    @property
    def tupletBracketThickness(self) -> int | float | None:
        """Thickness of tuplet brackets."""
        return self._getValue('tupletBracketThickness')

    @tupletBracketThickness.setter
    def tupletBracketThickness(self, value: int | float | None) -> None:
        self._setValue('tupletBracketThickness', value)

    def _getValue(self, name: str) -> int | float | tuple[str, ...] | None:
        # Common settings property getter.
        if not self._engravingDefaults:
            return None
        if name == 'textFontFamily':
            return self._engravingDefaults.get(name, ())
        if self.spaces:
            return self.font.smufl.toSpaces(
                self._engravingDefaults.get(name, None))
        return self._engravingDefaults.get(name, None)

    def _setValue(self,
                  name: str,
                  value: int | float | tuple[str, ...] | None) -> None:
        # Common settings property setter.
        # Keeps dynamic dict of settings in font.lib().
        value = normalizers.normalizeEngravingDefaultsAttr(name, value)
        if value is None:
            if self._engravingDefaults is None:
                return
            if (len(self._engravingDefaults) == 0
                    or len(self._engravingDefaults) == 1
                    and name in self._engravingDefaults):
                self.clear()
            else:
                self._engravingDefaults.pop(name)
        else:
            if self._engravingDefaults is None:
                self._engravingDefaults = {}
            self._engravingDefaults[name] = value
            if self.spaces:
                self._engravingDefaults[name] = self.font.smufl.toUnits(value)

    @property
    def _engravingDefaults(self) -> dict[str, int | float
                                         | tuple[str, ...] | None]:
        # Dynamic dict in font.lib.naked().
        if self._smufl.font is None:
            return None
        return self.font.lib.naked().get('_engravingDefaults')

    @_engravingDefaults.setter
    def _engravingDefaults(self, value: dict[str, int | float | tuple[str, ...]
                                             | None]) -> None:
        if value is None:
            self.font.lib.naked().pop('_engravingDefaults', None)
        else:
            self.font.lib.naked()['_engravingDefaults'] = value

    # -----------------------------
    # Normalization and Measurement
    # -----------------------------

    def round(self) -> None:
        """Round font units to integers.

        Method applies to the following attributes:

        * :attr:`arrowShaftThickness`
        * :attr:`barlineSeparation`
        * :attr:`beamSpacing`
        * :attr:`beamThickness`
        * :attr:`bracketThickness`
        * :attr:`dashedBarlineDashLength`
        * :attr:`dashedBarlineGapLength`
        * :attr:`dashedBarlineThickness`
        * :attr:`hairpinThickness`
        * :attr:`hBarThickness`
        * :attr:`legerLineExtension`
        * :attr:`legerLineThickness`
        * :attr:`lyricLineThickness`
        * :attr:`octaveLineThickness`
        * :attr:`pedalLineThickness`
        * :attr:`repeatBarlineDotSeparation`
        * :attr:`repeatEndingLineThickness`
        * :attr:`slurEndpointThickness`
        * :attr:`slurMidpointThickness`
        * :attr:`staffLineThickness`
        * :attr:`stemThickness`
        * :attr:`subBracketThickness`
        * :attr:`textEnclosureThickness`
        * :attr:`thickBarlineThickness`
        * :attr:`thinBarlineThickness`
        * :attr:`thinThickBarlineSeparation`
        * :attr:`tieEndpointThickness`
        * :attr:`tieMidpointThickness`
        * :attr:`tupletBracketThickness`

        If :attr:`spaces` is ``True``, values are left unchanged.

        Example::

            >>> f.smufl.engravingDefaults.stemThickness
            30.5
            >>> f.smufl.engravingDefaults.round()
            >>> f.smufl.engravingDefaults.stemThickness
            31

        ::

            >>> f.smufl.engravingDefaults.spaces = True
            >>> f.smufl.engravingDefaults.stemThickness
            0.12
            >>> f.smufl.engravingDefaults.round()
            >>> f.smufl.engravingDefaults.stemThickness
            0.12

        """
        if self.spaces:
            return

        for key in self.keys():
            attribute = getattr(self, key)
            if not isinstance(attribute, (int, float)):
                continue
            value = normalizers.normalizeVisualRounding(attribute)
            setattr(self, key, value)

    @property
    def spaces(self) -> bool:
        """Set state of measurement to staff spaces.

        Example::

            >>> f.smufl.engravingDefaults.stemThickness
            30.5
            >>> f.smufl.engravingDefaults.spaces = True
            >>> f.smufl.engravingDefaults.stemThickness
            0.12

        """
        if self._smufl is None:
            return None
        return self._smufl.spaces

    @spaces.setter
    def spaces(self, value: bool) -> None:
        self._smufl.spaces = value
