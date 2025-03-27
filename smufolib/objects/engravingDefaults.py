# pylint: disable=C0114, C0103, W0212, W0221
from __future__ import annotations
from typing import TYPE_CHECKING

from fontParts.base.base import BaseObject
from smufolib import normalizers, error

if TYPE_CHECKING:
    from smufolib.objects.smufl import Smufl
    from smufolib.objects.glyph import Glyph
    from smufolib.objects.font import Font
    from smufolib.objects.layer import Layer

# Type aliases
EngravingDefaultsValue = int | float | tuple[str, ...] | None
EngravingDefaultsDict = dict[str, EngravingDefaultsValue]

#: Names of engraving defaults as specified in the SMuFL standard.
ENGRAVING_DEFAULTS_KEYS: set = {
    "arrowShaftThickness",
    "barlineSeparation",
    "beamSpacing",
    "beamThickness",
    "bracketThickness",
    "dashedBarlineDashLength",
    "dashedBarlineGapLength",
    "dashedBarlineThickness",
    "hairpinThickness",
    "hBarThickness",
    "legerLineExtension",
    "legerLineThickness",
    "lyricLineThickness",
    "octaveLineThickness",
    "pedalLineThickness",
    "repeatBarlineDotSeparation",
    "repeatEndingLineThickness",
    "slurEndpointThickness",
    "slurMidpointThickness",
    "staffLineThickness",
    "stemThickness",
    "subBracketThickness",
    "textFontFamily",
    "textEnclosureThickness",
    "thickBarlineThickness",
    "thinBarlineThickness",
    "thinThickBarlineSeparation",
    "tieEndpointThickness",
    "tieMidpointThickness",
    "tupletBracketThickness",
}


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

    def _init(self, smufl: Smufl | None = None) -> None:
        self._smufl = smufl

    def _reprContents(self) -> list[str]:
        contents = []
        contents.append("in font")
        # pylint: disable-next=W0212
        if self.font is not None:
            contents += self.font._reprContents()
        return contents

    def naked(self):
        # BaseObject override for __eq__ and __hash__
        return self

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
        if self.font is not None:
            self.font.lib.naked().pop("com.smufolib.engravingDefaults")

    def items(self) -> EngravingDefaultsDict:
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
        return sorted(ENGRAVING_DEFAULTS_KEYS)

    def update(
        self,
        other: EngravingDefaults | EngravingDefaultsDict | None = None,
        **kwargs: EngravingDefaultsValue,
    ) -> None:
        r"""Update settings attributes with other object or values.

        :param other: Other :class:`EngravingDefaults` or :class:`dict`
            of attribute names mapped to values. Defaults to `None`.
        :param \**kwargs: Attribute names and values to update as
         keyword arguments.

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
        if not other or self.font is None:
            return

        self.font.lib["com.smufolib.engravingDefaults"] = {}
        for key, value in other.items():  # type: ignore[misc]
            if key not in self.keys():
                self.font.lib.pop("com.smufolib.engravingDefaults")
                raise AttributeError(
                    error.generateErrorMessage(
                        "attributeError", objectName=type(self).__name__, attribute=key
                    )
                )

            normalizedValue = normalizers.normalizeEngravingDefaultsAttr(key, value)
            if (
                self.smufl is not None
                and isinstance(normalizedValue, (int, float))
                and self.spaces
            ):
                normalizedValue = self.smufl.toUnits(normalizedValue)
            self.font.lib["com.smufolib.engravingDefaults"][key] = normalizedValue

    def _normalizeOthers(
        self,
        other: EngravingDefaults | EngravingDefaultsDict | None,
        kwargs: EngravingDefaultsDict,
    ) -> EngravingDefaultsDict | None:
        # Normalize update(other)
        if isinstance(other, EngravingDefaults):
            other = other.items()
        if other is None:
            other = {}
            if not kwargs:
                return None

        error.validateType(
            other,
            (EngravingDefaults, dict, type(None)),
            f"{self.__class__.__name__}.update()",
        )

        other |= kwargs
        return other

    def values(self) -> list[EngravingDefaultsValue]:
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
        if self._smufl is None:
            return None
        return normalizers.normalizeSmufl(self._smufl)

    @smufl.setter
    def smufl(self, value: Smufl) -> None:
        if self._smufl is not None and self._smufl != value:
            raise AssertionError(
                "Smufl for EngravingDefaults object is "
                "already set and is not same as value."
            )
        self._smufl = normalizers.normalizeSmufl(value)

    @property
    def font(self) -> Font | None:
        """Parent :class:`~smufolib.objects.font.Font` object."""
        if self._smufl is None:
            return None
        return self._smufl.font

    @font.setter
    def font(self, value: Font) -> None:
        if (
            self.smufl is not None
            and self.smufl.font is not None
            and self.smufl.font != value
        ):
            raise AssertionError(
                "Font for EngravingDefaults object is "
                "already set and is not same as value."
            )
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
        return self._getValue("arrowShaftThickness")  # type: ignore

    @arrowShaftThickness.setter
    def arrowShaftThickness(self, value: int | float | None) -> None:
        self._setValue("arrowShaftThickness", value)

    @property
    def barlineSeparation(self) -> int | float | None:
        """Distance between multiple thin barlines."""
        return self._getValue("barlineSeparation")  # type: ignore

    @barlineSeparation.setter
    def barlineSeparation(self, value: int | float | None) -> None:
        self._setValue("barlineSeparation", value)

    @property
    def beamSpacing(self) -> int | float | None:
        """Distance between beams."""
        return self._getValue("beamSpacing")  # type: ignore

    @beamSpacing.setter
    def beamSpacing(self, value: int | float | None) -> None:
        self._setValue("beamSpacing", value)

    @property
    def beamThickness(self) -> int | float | None:
        """Thickness of a beam."""
        return self._getValue("beamThickness")  # type: ignore

    @beamThickness.setter
    def beamThickness(self, value: int | float | None) -> None:
        self._setValue("beamThickness", value)

    @property
    def bracketThickness(self) -> int | float | None:
        """Thickness of the vertical line of a grouping bracket."""
        return self._getValue("bracketThickness")  # type: ignore

    @bracketThickness.setter
    def bracketThickness(self, value: int | float | None) -> None:
        self._setValue("bracketThickness", value)

    @property
    def dashedBarlineDashLength(self) -> int | float | None:
        """Length of the dashes to be used in a dashed barline."""
        return self._getValue("dashedBarlineDashLength")  # type: ignore

    @dashedBarlineDashLength.setter
    def dashedBarlineDashLength(self, value: int | float | None) -> None:
        self._setValue("dashedBarlineDashLength", value)

    @property
    def dashedBarlineGapLength(self) -> int | float | None:
        """Length of the gap between dashes in a dashed barline."""
        return self._getValue("dashedBarlineGapLength")  # type: ignore

    @dashedBarlineGapLength.setter
    def dashedBarlineGapLength(self, value: int | float | None) -> None:
        self._setValue("dashedBarlineGapLength", value)

    @property
    def dashedBarlineThickness(self) -> int | float | None:
        """Thickness of a dashed barline."""
        return self._getValue("dashedBarlineThickness")  # type: ignore

    @dashedBarlineThickness.setter
    def dashedBarlineThickness(self, value: int | float | None) -> None:
        self._setValue("dashedBarlineThickness", value)

    @property
    def hairpinThickness(self) -> int | float | None:
        """Thickness of a crescendo/diminuendo hairpin."""
        return self._getValue("hairpinThickness")  # type: ignore

    @hairpinThickness.setter
    def hairpinThickness(self, value: int | float | None) -> None:
        self._setValue("hairpinThickness", value)

    @property
    def hBarThickness(self) -> int | float | None:
        """Thickness of a crescendo/diminuendo hairpin."""
        return self._getValue("hBarThickness")  # type: ignore

    @hBarThickness.setter
    def hBarThickness(self, value: int | float | None) -> None:
        self._setValue("hBarThickness", value)

    @property
    def legerLineExtension(self) -> int | float | None:
        """Amount of leger line extension from notehead."""
        return self._getValue("legerLineExtension")  # type: ignore

    @legerLineExtension.setter
    def legerLineExtension(self, value: int | float | None) -> None:
        self._setValue("legerLineExtension", value)

    @property
    def legerLineThickness(self) -> int | float | None:
        """Thickness of a leger line."""
        return self._getValue("legerLineThickness")  # type: ignore

    @legerLineThickness.setter
    def legerLineThickness(self, value: int | float | None) -> None:
        self._setValue("legerLineThickness", value)

    @property
    def lyricLineThickness(self) -> int | float | None:
        """Thickness of the lyric extension line."""
        return self._getValue("lyricLineThickness")  # type: ignore

    @lyricLineThickness.setter
    def lyricLineThickness(self, value: int | float | None) -> None:
        self._setValue("lyricLineThickness", value)

    @property
    def octaveLineThickness(self) -> int | float | None:
        """Thickness of the dashed line used for an octave line."""
        return self._getValue("octaveLineThickness")  # type: ignore

    @octaveLineThickness.setter
    def octaveLineThickness(self, value: int | float | None) -> None:
        self._setValue("octaveLineThickness", value)

    @property
    def pedalLineThickness(self) -> int | float | None:
        """Thickness of the line used for piano pedaling."""
        return self._getValue("pedalLineThickness")  # type: ignore

    @pedalLineThickness.setter
    def pedalLineThickness(self, value: int | float | None) -> None:
        self._setValue("pedalLineThickness", value)

    @property
    def repeatBarlineDotSeparation(self) -> int | float | None:
        """Distance between dots and inner line of a repeat barline."""
        return self._getValue("repeatBarlineDotSeparation")  # type: ignore

    @repeatBarlineDotSeparation.setter
    def repeatBarlineDotSeparation(self, value: int | float | None) -> None:
        self._setValue("repeatBarlineDotSeparation", value)

    @property
    def repeatEndingLineThickness(self) -> int | float | None:
        """Thickness of repeat ending brackets."""
        return self._getValue("repeatEndingLineThickness")  # type: ignore

    @repeatEndingLineThickness.setter
    def repeatEndingLineThickness(self, value: int | float | None) -> None:
        self._setValue("repeatEndingLineThickness", value)

    @property
    def slurEndpointThickness(self) -> int | float | None:
        """Thickness of the end of a slur."""
        return self._getValue("slurEndpointThickness")  # type: ignore

    @slurEndpointThickness.setter
    def slurEndpointThickness(self, value: int | float | None) -> None:
        self._setValue("slurEndpointThickness", value)

    @property
    def slurMidpointThickness(self) -> int | float | None:
        """Thickness of the mid-point of a slur."""
        return self._getValue("slurMidpointThickness")  # type: ignore

    @slurMidpointThickness.setter
    def slurMidpointThickness(self, value: int | float | None) -> None:
        self._setValue("slurMidpointThickness", value)

    @property
    def staffLineThickness(self) -> int | float | None:
        """Thickness of each staff line."""
        return self._getValue("staffLineThickness")  # type: ignore

    @staffLineThickness.setter
    def staffLineThickness(self, value: int | float | None) -> None:
        self._setValue("staffLineThickness", value)

    @property
    def stemThickness(self) -> int | float | None:
        """Thickness of a stem."""
        return self._getValue("stemThickness")  # type: ignore

    @stemThickness.setter
    def stemThickness(self, value: int | float | None) -> None:
        self._setValue("stemThickness", value)

    @property
    def subBracketThickness(self) -> int | float | None:
        """Thickness of the vertical line of a grouping sub-bracket."""
        return self._getValue("subBracketThickness")  # type: ignore

    @subBracketThickness.setter
    def subBracketThickness(self, value: int | float | None) -> None:
        self._setValue("subBracketThickness", value)

    @property
    def textFontFamily(self) -> tuple[str, ...]:
        """tuple of text font pairings."""
        return self._getValue("textFontFamily")  # type: ignore

    @textFontFamily.setter
    def textFontFamily(self, value: tuple[str, ...]) -> None:
        self._setValue("textFontFamily", value)

    @property
    def textEnclosureThickness(self) -> int | float | None:
        """Thickness of box drawn around text instructions."""
        return self._getValue("textEnclosureThickness")  # type: ignore

    @textEnclosureThickness.setter
    def textEnclosureThickness(self, value: int | float | None) -> None:
        self._setValue("textEnclosureThickness", value)

    @property
    def thickBarlineThickness(self) -> int | float | None:
        """Thickness of a thick barline."""
        return self._getValue("thickBarlineThickness")  # type: ignore

    @thickBarlineThickness.setter
    def thickBarlineThickness(self, value: int | float | None) -> None:
        self._setValue("thickBarlineThickness", value)

    @property
    def thinBarlineThickness(self) -> int | float | None:
        """Thickness of a thin barline."""
        return self._getValue("thinBarlineThickness")  # type: ignore

    @thinBarlineThickness.setter
    def thinBarlineThickness(self, value: int | float | None) -> None:
        self._setValue("thinBarlineThickness", value)

    @property
    def thinThickBarlineSeparation(self) -> int | float | None:
        """Thickness of a thin barline."""
        return self._getValue("thinThickBarlineSeparation")  # type: ignore

    @thinThickBarlineSeparation.setter
    def thinThickBarlineSeparation(self, value: int | float | None) -> None:
        self._setValue("thinThickBarlineSeparation", value)

    @property
    def tieEndpointThickness(self) -> int | float | None:
        """Thickness of the end of a tie."""
        return self._getValue("tieEndpointThickness")  # type: ignore

    @tieEndpointThickness.setter
    def tieEndpointThickness(self, value: int | float | None) -> None:
        self._setValue("tieEndpointThickness", value)

    @property
    def tieMidpointThickness(self) -> int | float | None:
        """Thickness of the mid-point of a tie."""
        return self._getValue("tieMidpointThickness")  # type: ignore

    @tieMidpointThickness.setter
    def tieMidpointThickness(self, value: int | float | None) -> None:
        self._setValue("tieMidpointThickness", value)

    @property
    def tupletBracketThickness(self) -> int | float | None:
        """Thickness of tuplet brackets."""
        return self._getValue("tupletBracketThickness")  # type: ignore

    @tupletBracketThickness.setter
    def tupletBracketThickness(self, value: int | float | None) -> None:
        self._setValue("tupletBracketThickness", value)

    def _getValue(self, name: str) -> EngravingDefaultsValue:
        # Common settings property getter.
        if not self._engravingDefaults:
            return () if name == "textFontFamily" else None

        value = self._engravingDefaults.get(name, None)
        if name == "textFontFamily":
            value = self._engravingDefaults.get(name, ())

        elif self.spaces and isinstance(value, (int, float)) and self.font is not None:
            return self.font.smufl.toSpaces(value)
        return value

    def _setValue(self, name: str, value: EngravingDefaultsValue) -> None:
        # Common settings property setter.
        # Keeps dynamic dict of settings in font.lib().
        value = normalizers.normalizeEngravingDefaultsAttr(name, value)

        self._engravingDefaults = {}

        if self.font is None:
            raise AttributeError(
                error.generateErrorMessage(
                    "missingDependencyError", objectName=name, dependency="font"
                )
            )
        if not value:
            self._engravingDefaults.pop(name, None)

        elif self.spaces and isinstance(value, (int, float)) and self.font is not None:
            self._engravingDefaults[name] = self.font.smufl.toUnits(value)
        else:
            self._engravingDefaults[name] = value

    @property
    def _engravingDefaults(self) -> dict[str, EngravingDefaultsValue]:
        # Dynamic dict in font.lib.naked().
        if self.font is None:
            return {}
        return self.font.lib.naked().get("com.smufolib.engravingDefaults", {})

    @_engravingDefaults.setter
    def _engravingDefaults(self, value: EngravingDefaultsDict) -> None:
        if self.font is not None:
            self.font.lib.naked()["com.smufolib.engravingDefaults"] = value

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

        If :attr:`spaces` is :obj:`True`, values are left unchanged.

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
        if self.smufl is None:
            return False
        return self.smufl.spaces

    @spaces.setter
    def spaces(self, value: bool) -> None:
        if self.smufl is None:
            return
        self.smufl.spaces = value

    # ------------------------
    # Override from BaseObject
    # ------------------------

    def raiseNotImplementedError(self):
        """This exception needs to be raised frequently by
        the base classes. So, it's here for convenience.
        """
        raise NotImplementedError(
            error.generateErrorMessage(
                "notImplementedError", objectName=self.__class__.__name__
            )
        )
