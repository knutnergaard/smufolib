# pylint: disable=C0114, C0103, W0212, W0221
from __future__ import annotations
from typing import TYPE_CHECKING, cast
from collections.abc import Callable

from fontParts.base.base import BaseObject
from smufolib import config
from smufolib.objects import _lib
from smufolib.utils import error, normalizers
from smufolib.utils.rulers import DISPATCHER, ENGRAVING_DEFAULTS_MAPPING
from smufolib.utils._annotations import (
    CollectionType,
    EngravingDefaultsInput,
    EngravingDefaultsReturn,
)

if TYPE_CHECKING:  # pragma: no cover
    from smufolib.objects.smufl import Smufl
    from smufolib.objects.font import Font
    from smufolib.objects.glyph import Glyph
    from smufolib.objects.layer import Layer

# Type aliases
EngravingDefaultsDictInput = dict[str, EngravingDefaultsInput | None]
EngravingDefaultsDictReturn = dict[str, EngravingDefaultsReturn | None]

AUTO = config.load()["engravingDefaults"]["auto"]
ENGRAVING_DEFAULTS_LIB_KEY = "com.smufolib.engravingDefaults"

#: Names  and descriptions of engraving defaults as specified in the SMuFL standard.
ENGRAVING_DEFAULTS_ATTRIBUTES: dict[str, str] = {
    "textFontFamily": "Preferred text font families for pairing with this music font.",
    "staffLineThickness": "Thickness of each staff line.",
    "stemThickness": "Thickness of a stem.",
    "beamThickness": "Thickness of a beam.",
    "beamSpacing": "Distance between primary and secondary beams.",
    "legerLineThickness": "Thickness of a leger line.",
    "legerLineExtension": "Extension length of a leger line beyond the notehead.",
    "slurEndpointThickness": "Thickness at the end of a slur.",
    "slurMidpointThickness": "Thickness at the midpoint of a slur.",
    "tieEndpointThickness": "Thickness at the end of a tie.",
    "tieMidpointThickness": "Thickness at the midpoint of a tie.",
    "thinBarlineThickness": "Thickness of a thin barline.",
    "thickBarlineThickness": "Thickness of a thick barline.",
    "dashedBarlineThickness": "Thickness of a dashed barline.",
    "dashedBarlineDashLength": "Length of dashes in a dashed barline.",
    "dashedBarlineGapLength": "Gap length between dashes in a dashed barline.",
    "barlineSeparation": "Distance between multiple barlines when locked together.",
    "thinThickBarlineSeparation": "Distance between thin and thick barlines when locked together.",
    "repeatBarlineDotSeparation": "Horizontal distance between dots and barline in repeats.",
    "bracketThickness": "Thickness of bracket lines grouping staves.",
    "subBracketThickness": "Thickness of sub-bracket lines for related staves.",
    "hairpinThickness": "Thickness of crescendo/diminuendo hairpins.",
    "octaveLineThickness": "Thickness of dashed lines used for octave indications.",
    "pedalLineThickness": "Thickness of lines used for piano pedaling.",
    "repeatEndingLineThickness": "Thickness of brackets indicating repeat endings.",
    "arrowShaftThickness": "Thickness of arrow shafts.",
    "lyricLineThickness": "Thickness of lyric extension lines for melismas.",
    "textEnclosureThickness": "Thickness of boxes drawn around text instructions.",
    "tupletBracketThickness": "Thickness of brackets around tuplet numbers.",
    "hBarThickness": "Thickness of the H-bar in a multi-bar rest.",
}


class EngravingDefaults(BaseObject):
    """SMuFL engraving default settings.

    This object contains properties and methods pertained to SMuFL's
    :smufl:`engravingDefaults <specification/engravingdefaults.html>` metadata
    structure, defining recommended defaults for line widths etc., according to the
    specification.

    The :class:`EngravingDefaults` object is essentially a :class:`dict` with each
    engraving default setting exposed as a read/write property.

    .. versionchanged:: 0.5.0

        If a value is unassigned (or explicitly set to :obj:`None`), the attribute will
        be calculated automatically from the corresponding glyph in the font, provided
        that glyph exists and :attr:`auto` is enabled. See
        :data:`.ENGRAVING_DEFAULTS_MAPPING` for a complete list of attributes and their
        default corresponding glyphs and assigned ruler functions.

    .. tip::

        Optionally, values may be explicitly set using glyph-based calculations provided
        by the :mod:`~bin.calculateEngravingDefaults` script.

    :param smufl: Parent :class:`~smufolib.objects.smufl.Smufl` object.
    :param auto: Whether to calculate engraving defaults automatically. Defaults to
        :confval:`engravingDefaults.auto` configuration.

    This object is typically accessed through a font's Smufl metadata interface:

        >>> engravingDefaults = font.smufl.engravingDefaults
        >>> glyph = font["uniE050"]
        >>> engravingDefaults = glyph.smufl.engravingDefaults

    It may also be instantiated independently and assigned to a font later:

        >>> engravingDefaults = EngravingDefaults()  # doctest: +SKIP

    """

    # Stubs to improve linting support.
    arrowShaftThickness: int | float
    barlineSeparation: int | float
    beamSpacing: int | float
    beamThickness: int | float
    bracketThickness: int | float
    dashedBarlineDashLength: int | float
    dashedBarlineGapLength: int | float
    dashedBarlineThickness: int | float
    hairpinThickness: int | float
    hBarThickness: int | float
    legerLineExtension: int | float
    legerLineThickness: int | float
    lyricLineThickness: int | float
    octaveLineThickness: int | float
    pedalLineThickness: int | float
    repeatBarlineDotSeparation: int | float
    repeatEndingLineThickness: int | float
    slurEndpointThickness: int | float
    slurMidpointThickness: int | float
    staffLineThickness: int | float
    stemThickness: int | float
    subBracketThickness: int | float
    textEnclosureThickness: int | float
    thickBarlineThickness: int | float
    thinBarlineThickness: int | float
    thinThickBarlineSeparation: int | float
    tieEndpointThickness: int | float
    tieMidpointThickness: int | float
    tupletBracketThickness: int | float

    def _init(self, smufl: Smufl | None = None, auto: bool = AUTO) -> None:
        self._smufl = smufl
        self._auto = auto

    def _reprContents(self) -> list[str]:
        contents = []
        if self.font is not None:
            contents.append("in font")
            contents += self.font._reprContents()  # pylint: disable-next=W0212
            contents.append(f"auto={self._auto}")
        return contents

    def naked(self):
        """Return the wrapped defcon object.

        This method is useful if you need to bypass the wrapper and interact directly
        with the underlying `defcon <https://defcon.robotools.dev/en/stable/>`_ object
        (e.g., for compatibility with other libraries).

        Example:

            >>> engravingDefaults.glyph.naked()  # doctest: +ELLIPSIS
            <defcon.objects.glyph.Glyph object at 0x...>

        """
        return self  # pragma: no cover

    # -------
    # Parents
    # -------

    @property
    def smufl(self) -> Smufl | None:
        """Parent :class:`.smufl.Smufl` object.

        Example:

            >>> engravingDefaults.smufl  # doctest: +ELLIPSIS
            <Smufl in glyph 'uniE050' ['gClef'] ('public.default') at ...>


        """
        return self._smufl

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
        """Parent :class:`.Font` object.

        Example:

            >>> engravingDefaults.font  # doctest: +ELLIPSIS
            <Font 'MyFont Regular' path='/path/to/MyFont.ufo' at ...>

        """
        if self._smufl is None:
            return None
        return self._smufl.font

    @property
    def glyph(self) -> Glyph | None:
        """Parent :class:`.Glyph` object.

        Example:

            >>> engravingDefaults.glyph  # doctest: +ELLIPSIS
            <Glyph 'uniE050' ['gClef'] ('public.default') at ...>

        """
        if self._smufl is None:
            return None
        return self._smufl.glyph

    @property
    def layer(self) -> Layer | None:
        """Parent :class:`.Layer` object.

        Example:

        >>> engravingDefaults.layer  # doctest: +ELLIPSIS
        <Layer 'public.default' at ...>

        """
        if self._smufl is None:
            return None
        return self._smufl.layer

    # ----
    # Auto
    # ----

    @property
    def auto(self) -> bool:
        """Whether to calculate engraving defaults automatically.

        When :obj:`True`, engraving defaults are calculated automatically from font
        measurements. When :obj:`False`, all values must be set explicitly.

        Automatically calculated values are overridden by any explicitly set defaults,
        regardless of the `auto` setting.

        Example:

            >>> engravingDefaults.auto = False
            >>> engravingDefaults.auto
            False

        """
        return self._auto

    @auto.setter
    def auto(self, value: bool) -> None:
        self._auto = value

    # ------------------
    # Dictionary methods
    # ------------------

    def clear(self) -> None:
        """Clear all engraving default settings.

        If :confval:`engravingDefaults.auto` is enabled, values will fall back to
        automatically calculated values after being cleared.

        Example::

            >>> engravingDefaults.items()
            {'arrowShaftThickness': 46, 'barlineSeparation': 72, ...}
            >>> engravingDefaults.clear()
            >>> engravingDefaults.items()
            {'arrowShaftThickness': None, 'barlineSeparation': None, ...}

        """
        if self.font is not None:
            self.font.lib.naked().pop(ENGRAVING_DEFAULTS_LIB_KEY, None)

    def items(self) -> EngravingDefaultsDictReturn:
        """Return :class:`dict` of all available settings and their values.

        Example:

            >>> engravingDefaults.items()  # doctest: +ELLIPSIS
            {'arrowShaftThickness': 46, 'barlineSeparation': 72, ...}

        """
        return dict(zip(self.keys(), self.values()))

    def keys(self) -> list[str]:
        """Return sorted :class:`list` of all available settings names.

        Example:

            >>> engravingDefaults.keys()  # doctest: +ELLIPSIS
            ['arrowShaftThickness', 'barlineSeparation', ...]

        """
        return sorted(ENGRAVING_DEFAULTS_ATTRIBUTES)

    def update(
        self,
        other: EngravingDefaults | EngravingDefaultsDictInput | None = None,
        **kwargs: EngravingDefaultsInput | None,
    ) -> None:
        r"""Update settings attributes with other object or values.

        :param other: Other :class:`EngravingDefaults` or :class:`dict`
            of attribute names mapped to values. Defaults to `None`.
        :param \**kwargs: Attribute names and values to update as
         keyword arguments.

        An object may be updated in a few different ways:

            >>> engravingDefaults.items()  # doctest: +ELLIPSIS
            {'arrowShaftThickness': 46, 'barlineSeparation': 72, ...}

        # Update with :class:`dict` object.:

            >>> other = {"arrowShaftThickness": 35, "barlineSeparation": 68}
            >>> engravingDefaults.update(other)
            >>> engravingDefaults.items()  # doctest: +ELLIPSIS
            {'arrowShaftThickness': 35, 'barlineSeparation': 68, ...}

        Update with other :class:`EngravingDefaults` object.:

            >>> other = otherFont.smufl.engravingDefaults
            >>> other.items()
            {'arrowShaftThickness': 52, 'barlineSeparation': 75, ...}
            >>> engravingDefaults.update(other)
            >>> engravingDefaults.items()  # doctest: +ELLIPSIS
            {'arrowShaftThickness': 52, 'barlineSeparation': 75, ...}

        Update with keyword arguments:

            >>> engravingDefaults.update(arrowShaftThickness=46, barlineSeparation=72)
            >>> engravingDefaults.items()  # doctest: +ELLIPSIS
            {'arrowShaftThickness': 46, 'barlineSeparation': 72, ...}

        """
        normalizedOther = self._mergeOthers(other, kwargs)
        if not normalizedOther or self.font is None:
            return

        if ENGRAVING_DEFAULTS_LIB_KEY not in self.font.lib:
            self.font.lib[ENGRAVING_DEFAULTS_LIB_KEY] = {}

        for key, value in normalizedOther.items():
            if key not in self.keys():
                raise AttributeError(
                    error.generateErrorMessage(
                        "attributeError", objectName=type(self).__name__, attribute=key
                    )
                )

            normalizedValue = normalizers.normalizeEngravingDefaultsAttr(key, value)
            if value is None:
                continue
            if (
                self._smufl is not None
                and isinstance(normalizedValue, (int, float))
                and self.spaces
            ):
                normalizedValue = self._smufl.toUnits(normalizedValue)
            self.font.lib[ENGRAVING_DEFAULTS_LIB_KEY][key] = normalizedValue

    def _mergeOthers(
        self,
        other: EngravingDefaults | EngravingDefaultsDictInput | None,
        kwargs: EngravingDefaultsDictInput,
    ) -> EngravingDefaultsDictInput | None:
        error.validateType(
            other,
            (EngravingDefaults, dict, type(None)),
            f"{self.__class__.__name__}.update()",
        )

        base: dict
        if isinstance(other, EngravingDefaults):
            base = other.items()
        elif other is None:
            if not kwargs:
                return None
            base = {}
        else:
            base = other

        base |= kwargs
        return base

    def values(self) -> list[EngravingDefaultsReturn]:
        """Return a :class:`list` of all available settings values.

        Order corresponds to :meth:`keys`.

        Example:

            >>> engravingDefaults.values()  # doctest: +ELLIPSIS
            [46, 72, ...]

        """
        return [getattr(self, k) for k in self.keys()]

    # ----------
    # Attributes
    # ----------

    @property
    def textFontFamily(self) -> tuple[str] | None:
        """Preferred text font families for pairing with this music font"""
        return cast(tuple[str] | None, self._getValue("textFontFamily"))

    @textFontFamily.setter
    def textFontFamily(self, value: CollectionType[str]) -> None:
        self._setValue("textFontFamily", value)

    # All other properties declared dynamically below

    def _getValue(self, key: str) -> EngravingDefaultsReturn | None:
        # Common settings property getter.
        libDict = _lib.getLibSubdict(self.font, ENGRAVING_DEFAULTS_LIB_KEY)
        if libDict is None or not libDict and not self._auto:
            return None

        value = libDict.get(key, None)
        if key == "textFontFamily":
            value = libDict.get(key, ())

        if self.font and value is None and self._auto:
            glyphName = ENGRAVING_DEFAULTS_MAPPING[key]["glyph"]
            try:
                glyph = self.font[glyphName]
            except KeyError:
                return None
            rulerName = ENGRAVING_DEFAULTS_MAPPING[key]["ruler"]
            ruler: Callable[["Glyph"], int | float | None] = DISPATCHER[rulerName]
            value = ruler(glyph)

        elif self.spaces and isinstance(value, (int, float)) and self.font is not None:
            return self.font.smufl.toSpaces(value)
        return value

    def _setValue(self, key: str, value: EngravingDefaultsInput | None) -> None:
        # Common settings property setter.
        # Keeps dynamic dict of settings in font.lib().

        if self.font is None:
            return

        normalized = normalizers.normalizeEngravingDefaultsAttr(key, value)

        if self.spaces and isinstance(normalized, (int, float)):
            normalized = self.font.smufl.toUnits(normalized)

        _lib.updateLibSubdictValue(
            self.font,
            ENGRAVING_DEFAULTS_LIB_KEY,
            key,
            normalized,
        )

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

        Example:

            >>> engravingDefaults.spaces = True
            >>> engravingDefaults.stemThickness = 0.12
            >>> engravingDefaults.round()
            >>> engravingDefaults.stemThickness
            0.12

            >>> engravingDefaults.spaces = False
            >>> engravingDefaults.stemThickness = 30.5
            >>> engravingDefaults.round()
            >>> engravingDefaults.stemThickness
            31

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
        """Whether to set state of measurement to staff spaces.

        Example:

            engravingDefaults.stemThickness = 25
            >>> engravingDefaults.spaces = True
            >>> engravingDefaults.stemThickness
            0.1
            >>> engravingDefaults.spaces = False
            >>> engravingDefaults.stemThickness
            25


        """
        if self._smufl is None:
            return False
        return self._smufl.spaces

    @spaces.setter
    def spaces(self, value: bool) -> None:
        if self._smufl is None:
            return
        self._smufl.spaces = value

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


def _makeProperty(attr: str, doc: str):
    # textFontFamily declared explicitly above

    def getter(self) -> int | float | None:
        return self._getValue(attr)

    def setter(self, value: int | float | None) -> None:
        self._setValue(attr, value)

    return property(getter, setter, doc=doc)


for name, description in ENGRAVING_DEFAULTS_ATTRIBUTES.items():
    if name != "textFontFamily":
        setattr(EngravingDefaults, name, _makeProperty(name, description))
