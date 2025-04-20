# pylint: disable=C0103, C0114, R0904, W0212, W0221
from __future__ import annotations
from typing import TYPE_CHECKING, Any
import re

from fontParts.base.base import BaseDict
from smufolib.utils import converters, error, normalizers

if TYPE_CHECKING:  # pragma: no cover
    from smufolib.objects.layer import Layer
    from smufolib.objects.font import Font
    from smufolib.objects.glyph import Glyph
    from smufolib.objects.smufl import Smufl

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


class Anchors(BaseDict):
    keyNormalizer = normalizers.normalizeAnchorName
    valueNormalizer = normalizers.normalizeAnchorValue

    def _init(self, smufl: Smufl | None = None) -> None:
        self._smufl = smufl
        self._cachedData: dict[str, tuple[int | float]] = {}

    def _reprContents(self) -> list[str]:
        contents = []
        if self.font is not None:
            contents.append("in Glyph")

            contents += self.glyph._reprContents()  # pylint: disable-next=W0212
        return contents

    def __str__(self) -> str:
        """String representation of the object."""
        return str(dict(self._items()))

    def naked(self):
        # BaseObject override for __eq__ and __hash__
        return self  # pragma: no cover

    # -------
    # Parents
    # -------

    @property
    def smufl(self) -> Smufl | None:
        """Parent :class:`~smufolib.objects.smufl.Smufl`."""
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
        """Parent :class:`~smufolib.objects.font.Font` object."""
        if self._smufl is None:
            return None
        return self._smufl.font

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

    # ------------------
    # Dictionary methods
    # ------------------

    def _items(self):
        self._rebuildData()
        return self._data.items()

    def _contains(self, key):
        return key in self._data

    def _setItem(self, key, value):
        if key in ANCHOR_NAMES:
            x, y = value
            x = self.smufl.toUnits(x) if self.smufl.spaces else x
            y = self.smufl.toUnits(y) if self.smufl.spaces else y
            self.glyph.appendAnchor(key, (x, y))

    def _getItem(self, key):
        return self._data[key]

    def _delItem(self, key):
        del self._data[key]

    def _rebuildData(self) -> dict[str, tuple[int | float]]:
        """The internal data dictionary."""
        self._cachedData.clear()
        if self.glyph and self.smufl:
            for a in self.glyph.naked().anchors:
                if a.name in ANCHOR_NAMES:
                    x = self.smufl.toSpaces(a.x) if self.smufl.spaces else a.x
                    y = self.smufl.toSpaces(a.y) if self.smufl.spaces else a.y

                    if x is None or y is None:
                        continue

                    self._cachedData[a.name] = (x, y)

        return self._cachedData

    @property
    def _data(self):
        if not self._cachedData:
            return self._rebuildData()
        return self._cachedData
