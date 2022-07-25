"""
Font metadata module for SMufoLib.
"""
from __future__ import annotations
from typing import Dict
from abc import abstractmethod

from fontParts.fontshell import RFont

from smufolib import config, converters, engraving
from smufolib.glyph import Glyph
from smufolib.request import Request

CONFIG = config.configLoad()


class Font(RFont):
    """
    Class representing a single Unified Font Object (UFO).

    `Font` is a read-only wrapper around a FontParts RFont object, adding
    SMuFL-specific font metadata and functionality. It preserves the
    dict-like behavior of RFont, making the object a dictionary of `Glyph`
    objects indexed on their names.

    :param pathOrObject: the filepath to UFO font file.
    :param showInterface: enable graphical interface.
    """

    # pylint: disable=too-many-ancestors, invalid-name

    def __init__(self,
                 pathOrObject: str | None = CONFIG['fontPaths']['ufo'],
                 showInterface: bool = False,
                 **kwargs) -> None:

        super().__init__(pathOrObject, showInterface, **kwargs)
        self.rFont: RFont = RFont(pathOrObject, showInterface)

    def __iter__(self):
        return iter(self._glyphs.values())

    def __getitem__(self, name):
        return self._glyphs[name]

    def __len__(self):
        return len(self._glyphs)

    def __contains__(self, name):
        return name in self._glyphs

    @abstractmethod
    def raiseNotImplementedError(self):
        pass

    def findGlyph(self, smuflName: str) -> Glyph | None:
        """
        Get Glyph object from smufl name.

        Initially checks glyphnames.json for matches. If glyph is
        private, the font itself is checked (currently a slow
        process).

        :param smuflName: SMuFL-specific canonical glyph name.
        """
        namesDict = Request(CONFIG['smuflUrls']['glyphnamesJson'],
                            CONFIG['smuflPaths']['glyphnamesJson']).json()
        try:
            codepoint = namesDict[smuflName]['codepoint']
            name = converters.toUniName(codepoint)
            return self[name]
        except KeyError:
            for glyph in self:
                if not glyph.smuflName == smuflName:
                    continue
                return glyph

    def spaces(self, units: int | float) -> float:
        """
        Convert font units to staff spaces based on font UPM size.
        """
        space = self.info.unitsPerEm / 4
        return round(float(units) / space, 3)

    @ property
    def engravingDefaults(self) -> Dict[str, str]:
        """
        SMuFL engraving defaults dictionary.

        Checks for values in config before extracting values with
        `engraving.get_engravingDefaults`. Converts any int
        to staff spaces.
        """
        if self.path:
            return {k: self.spaces(v) if isinstance(v, int) else v for
                    k, v in engraving.getEngravingDefaults(
                self, **CONFIG['engravingDefaults']).items()}
        return {}

    @property
    def name(self):
        """
        SMuFL-specific font name (font family Name).
        """
        return self.info.familyName

    @property
    def version(self):
        """
        SMuFL-specific font version number (major.minor).
        """
        return f'{self.info.versionMajor}.{self.info.versionMinor}'

    @ property
    def _glyphs(self) -> Dict[str, Glyph]:
        # Dictionary of Glyph objects indexed on glyph names.
        return {k: Glyph(k, self) for k in self.rFont.keys()}
