# pylint: disable=C0114, C0103, W0212, W0221
from __future__ import annotations
from typing import TYPE_CHECKING, cast
from collections.abc import Callable

from fontParts.base.base import BaseObject
from smufolib import config
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

#: Names  and descriptions of engraving defaults as specified in the SMuFL standard.
ENGRAVING_DEFAULTS_ATTRIBUTES: dict[str, str] = {
    "textFontFamily": "Preferred text font families for pairing with this music font",
    "staffLineThickness": "Thickness of each staff line",
    "stemThickness": "Thickness of a stem",
    "beamThickness": "Thickness of a beam",
    "beamSpacing": "Distance between primary and secondary beams",
    "legerLineThickness": "Thickness of a leger line",
    "legerLineExtension": "Extension length of a leger line beyond the notehead",
    "slurEndpointThickness": "Thickness at the end of a slur",
    "slurMidpointThickness": "Thickness at the midpoint of a slur",
    "tieEndpointThickness": "Thickness at the end of a tie",
    "tieMidpointThickness": "Thickness at the midpoint of a tie",
    "thinBarlineThickness": "Thickness of a thin barline",
    "thickBarlineThickness": "Thickness of a thick barline",
    "dashedBarlineThickness": "Thickness of a dashed barline",
    "dashedBarlineDashLength": "Length of dashes in a dashed barline",
    "dashedBarlineGapLength": "Gap length between dashes in a dashed barline",
    "barlineSeparation": "Distance between multiple barlines when locked together",
    "thinThickBarlineSeparation": "Distance between thin and thick barlines when locked together",
    "repeatBarlineDotSeparation": "Horizontal distance between dots and barline in repeats",
    "bracketThickness": "Thickness of bracket lines grouping staves",
    "subBracketThickness": "Thickness of sub-bracket lines for related staves",
    "hairpinThickness": "Thickness of crescendo/diminuendo hairpins",
    "octaveLineThickness": "Thickness of dashed lines used for octave indications",
    "pedalLineThickness": "Thickness of lines used for piano pedaling",
    "repeatEndingLineThickness": "Thickness of brackets indicating repeat endings",
    "arrowShaftThickness": "Thickness of arrow shafts",
    "lyricLineThickness": "Thickness of lyric extension lines for melismas",
    "textEnclosureThickness": "Thickness of boxes drawn around text instructions",
    "tupletBracketThickness": "Thickness of brackets around tuplet numbers",
    "hBarThickness": "Thickness of the H-bar in a multi-bar rest",
}


class EngravingDefaults(BaseObject):
    """SMuFL engraving default settings.

    This object contains properties and methods pertained to SMuFL's
    `engravingDefaults
    <https://w3c.github.io/smufl/latest/specification/engravingdefaults.html>`_
    metadata structure, defining recommended defaults for line widths
    etc., according to the specification.

    The :class:`EngravingDefaults` object is essentially a :class:`dict`
    with each engraving default setting exposed as a read/write property.

    .. versionadded:: 0.5.0

        If a value is unassigned (or explicitly set to :obj:`None`), the attribute
        will be calculated automatically from the corresponding glyph in the font,
        provided that glyph exists and the :ref:`[engravingDefaults]` `auto`
        setting is enabled in the configuration file.
        See :ref:`engraving-defaults-mapping` for a complete list of attributes and
        their default corresponding glyphs and assigned ruler functions.

    .. tip::

        Optionally, values may be explicitly set using glyph-based calculations provided
        by the :mod:`~bin.calculateEngravingDefaults` script.

    :param smufl: Parent :class:`~smufolib.objects.smufl.Smufl` object.

    While this object is normally created as part of
    a :class:`~smufolib.objects.font.Font`, an orphan :class:`EngravingDefaults`
    object may be created like this::

        >>> d = EngravingDefaults()

    """

    def _init(self, smufl: Smufl | None = None) -> None:
        self._smufl = smufl

    def _reprContents(self) -> list[str]:
        contents = []
        if self.font is not None:
            contents.append("in font")
            contents += self.font._reprContents()  # pylint: disable-next=W0212
            contents.append(f"auto={_getAutoFlag()}")
        return contents

    def naked(self):
        # BaseObject override for __eq__ and __hash__
        return self  # pragma: no cover

    # -------
    # Parents
    # -------

    @property
    def smufl(self) -> Smufl | None:
        """Parent :class:`.smufl.Smufl` object"""
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
        """Parent :class:`.Font` object"""
        if self._smufl is None:
            return None
        return self._smufl.font

    @property
    def glyph(self) -> Glyph | None:
        """Parent :class:`.Glyph` object"""
        if self._smufl is None:
            return None
        return self._smufl.glyph

    @property
    def layer(self) -> Layer | None:
        """Parent :class:`.Layer` object"""
        if self._smufl is None:
            return None
        return self._smufl.layer

    # ------------------
    # Dictionary methods
    # ------------------

    def clear(self) -> None:
        """Clear all engraving default settings.

        If `auto` is enabled in :ref:`[engravingDefaults]`, values will fall back to
        automatically calculated values after being cleared.

        Example::

            >>> d.items()
            {'arrowShaftThickness': 46, 'barlineSeparation': 72, ...}
            >>> d.clear()
            >>> d.items()
            {'arrowShaftThickness': None, 'barlineSeparation': None, ...}

        """
        if self.font is not None:
            self.font.lib.naked().pop("com.smufolib.engravingDefaults", None)

    def items(self) -> EngravingDefaultsDictReturn:
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
        normalizedOther = self._mergeOthers(other, kwargs)
        if not normalizedOther or self.font is None:
            return

        if "com.smufolib.engravingDefaults" not in self.font.lib:
            self.font.lib["com.smufolib.engravingDefaults"] = {}

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
            self.font.lib["com.smufolib.engravingDefaults"][key] = normalizedValue

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
        """Return list of all available settings values.

        Order corresponds to :meth:`keys`.

        Example::

            >>> d = f.smufl.engravingDefaults
            >>> d.values()
            [46, 72, 62, 125, 125, 125, 57, 36, 200, 39, 80, 40, ...]

        """
        return [getattr(self, k) for k in self.keys()]

    # ----------
    # Properties
    # ----------

    @property
    def textFontFamily(self) -> tuple[str] | None:
        """Preferred text font families for pairing with this music font"""
        return cast(tuple[str] | None, self._getValue("textFontFamily"))

    @textFontFamily.setter
    def textFontFamily(self, value: CollectionType[str]) -> None:
        self._setValue("textFontFamily", value)

    # All other properties declared dynamically below

    def _getValue(self, name: str) -> EngravingDefaultsReturn | None:
        # Common settings property getter.
        if not self._libDict and not _getAutoFlag():
            return None

        value = self._libDict.get(name, None)
        if name == "textFontFamily":
            value = self._libDict.get(name, ())

        if self.font and value is None and _getAutoFlag():
            glyphName = ENGRAVING_DEFAULTS_MAPPING[name]["glyph"]
            try:
                glyph = self.font[glyphName]
            except KeyError:
                return None
            rulerName = ENGRAVING_DEFAULTS_MAPPING[name]["ruler"]
            ruler: Callable[["Glyph"], int | float | None] = DISPATCHER[rulerName]
            value = ruler(glyph)

        elif self.spaces and isinstance(value, (int, float)) and self.font is not None:
            return self.font.smufl.toSpaces(value)
        return value

    def _setValue(self, name: str, value: EngravingDefaultsInput | None) -> None:
        # Common settings property setter.
        # Keeps dynamic dict of settings in font.lib().

        if self.font is None:
            return

        normalizedValue = normalizers.normalizeEngravingDefaultsAttr(name, value)
        libDict = self._libDict

        if not normalizedValue:
            libDict.pop(name, None)

            if not libDict:
                self.font.lib.pop("com.smufolib.engravingDefaults", None)
            else:
                self._libDict = libDict

        else:
            if self.spaces and isinstance(normalizedValue, (int, float)):
                normalizedValue = self.font.smufl.toUnits(normalizedValue)

            self._libDict[name] = normalizedValue
            self._libDict = libDict

    @property
    def _libDict(self) -> EngravingDefaultsDictReturn:
        # Dynamic dict in font.lib.naked().
        if self.font is None:
            return {}
        lib = self.font.lib.naked()
        return lib.setdefault("com.smufolib.engravingDefaults", {})

    @_libDict.setter
    def _libDict(self, value: EngravingDefaultsDictInput) -> None:
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


def _getAutoFlag():
    return config.load()["engravingDefaults"]["auto"]


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
