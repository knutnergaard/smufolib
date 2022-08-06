"""Glyph metadata module for SMufoLib."""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple
import ast
import re

from fontParts.fontshell import RGlyph, RAnchor

from smufolib import config, converters
from smufolib.range import Range
from smufolib.request import Request
if TYPE_CHECKING:
    from smufolib.font import Font

CONFIG = config.configLoad()


class Glyph:
    """Glyph-related info and metadata.

    :param name: the glyph's name.
    :param font: the glyph's parent font object.
    """

    # pylint: disable=invalid-name, too-many-public-methods

    def __init__(self,
                 name: str | None = None,
                 font: Font | None = None) -> None:

        self.name = name
        self.font = font

    def __repr__(self):
        return (f"<{self.__class__.__name__} '{self.name}' "
                f"('{self.smuflName}') at {id(self)}>")

    def appendAnchor(self, name: str | None = None,
                     position: List[float] | None = None,
                     color: Tuple[int] | None = None,
                     rAnchor: RAnchor | None = None):
        """Append SMuFL formatted anchor point to glyph.
        :param name: anchor name.
        :param position: anchor position in staff spaces.
        :param color: anchor color
        :param rAnchor: template base anchor object.
        """
        position = tuple(self.font.toUnits(n) for n in position)
        return self.rGlyph.appendAnchor(name=name, position=position,
                                        color=color, anchor=rAnchor)

    # ===================
    # Metadata properties
    # ===================

    @property
    def advanceWidth(self) -> float:
        """Glyph advance width in staff spaces."""
        return self.font.toSpaces(float(self.rGlyph.width))

    @property
    def alternates(self) -> Tuple[Dict[str, str]]:
        """Metadata of glyph alternates."""
        pattern = fr'\b{self.name}(?:\.salt[0-9]{{2}}|\.ss[0-9]{{2}})\b'
        string = ' '.join(sorted(self.font.keys()))
        results = re.findall(pattern, string)
        alternates = []
        for name in results:
            glyph = Glyph(name, self.font)
            alternates.append({'codepoint': glyph.codepoint,
                               'name': glyph.name})
        return tuple(alternates)

    @property
    def anchors(self) -> Dict[str, Tuple[float]]:
        """Glyph anchors as Cartesian coordinates in staff spaces."""
        return {a.name: (self.font.toSpaces(a.x),
                         self.font.toSpaces(a.y)) for a in self.rGlyph.anchors}

    @property
    def bBox(self) -> Dict[str, Tuple[float]]:
        """Glyph bounding box as Cartesian coordinates in spaces."""
        if not self.rGlyph.bounds:
            return None
        xMin, yMin, xMax, yMax = self.rGlyph.bounds
        return {"bBoxSW": (self.font.toSpaces(xMin), self.font.toSpaces(yMin)),
                "bBoxNE": (self.font.toSpaces(xMax), self.font.toSpaces(yMax))}

    @property
    def codepoint(self) -> str | None:
        """Format hexadecimal codepoint, e.g., U+E023."""
        if not self.rGlyph.unicode:
            return None
        return converters.toUniHex(self.rGlyph.unicode)

    @property
    def components(self) -> Tuple[str]:
        """Ligature components as smufl glyph names."""
        if '_' not in self.name:
            return ()
        names = self.name.split('_')
        components = []
        for name in names:
            if name not in self.font:
                continue
            glyph = Glyph(name, self.font)
            if not glyph.smuflName:
                continue
            components.append(glyph.smuflName)
        return tuple(components)

    # =====================
    # Annotation properties
    # =====================

    @property
    def annotation(self) -> Dict[str, str | Tuple[str]]:
        """Master annotation dictionary.

        This is where all individual annotation properties live. It is
        sourced from RGlyph.note, which in turn must be a valid
        dictionary, recognizable by ast.literal_eval.
        """
        if not self.rGlyph.note:
            return {}
        try:
            return ast.literal_eval(self.rGlyph.note)
        except (SyntaxError, ValueError):
            return {}

    @annotation.setter
    def annotation(self, value):
        if value is None:
            self.rGlyph.note = value
        elif not isinstance(value, dict):
            typename = type(value).__name__
            raise TypeError(f'annotation must be dict, not {typename}')
        else:
            self.rGlyph.note = str(value)

    @property
    def classes(self) -> Tuple[str]:
        """
        SMuFL-specific class memberships.
        """
        return tuple(self.annotation.get('classes', ()))

    @classes.setter
    def classes(self, value):
        annotation = self.annotation
        annotation['classes'] = value
        if not value:
            annotation.pop('classes', None)
        self.annotation = annotation

    @classes.deleter
    def classes(self):
        annotation = self.annotation
        del annotation['classes']
        self.annotation = annotation

    @property
    def description(self) -> str | None:
        """SMuFL-specific glyph description of optional glyphs."""
        return self.annotation.get('description', None)

    @description.setter
    def description(self, value):
        annotation = self.annotation
        annotation['description'] = value
        if not value:
            annotation.pop('description', None)
        self.annotation = annotation

    @description.deleter
    def description(self):
        annotation = self.annotation
        del annotation['description']
        self.annotation = annotation

    @property
    def note(self) -> str | None:
        """Arbitrary glyph note field."""
        return self.annotation.get('note', None)

    @note.setter
    def note(self, value):
        annotation = self.annotation
        annotation['note'] = value
        if not value:
            annotation.pop('note', None)
        self.annotation = annotation

    @note.deleter
    def note(self):
        annotation = self.annotation
        del annotation['note']
        self.annotation = annotation

    @property
    def smuflName(self) -> str | None:
        """SMuFL-specific canonical glyph name."""
        return self.annotation.get('name', None)

    @smuflName.setter
    def smuflName(self, value):
        annotation = self.annotation
        annotation['name'] = value
        if not value:
            annotation.pop('name', None)
        self.annotation = annotation

    @smuflName.deleter
    def smuflName(self):
        annotation = self.annotation
        del annotation['name']
        self.annotation = annotation

    # =====================
    # Validation properties
    # =====================

    @property
    def isLigature(self) -> bool:
        """Return True if ligature."""
        if self.name.count('uni') > 1 and '_' in self.name:
            return True
        return False

    @property
    def isOptional(self) -> bool:
        """Return True if optional glyph."""
        if self.rGlyph.unicode and 0xF400 <= self.rGlyph.unicode <= 0xF8FF:
            return True
        return False

    @property
    def isSalt(self) -> bool:
        """Return True if stylistic alternate glyph."""
        if self.name.endswith('.salt', 7, -2):
            return True
        return False

    @property
    def isSet(self) -> bool:
        """Return True if stylistic set glyph."""
        if self.name.endswith('.ss', 7, -2):
            return True
        return False

    # ==================
    # General properties
    # ==================

    @property
    def base(self) -> Glyph:
        """Glyph object of alternate's base glyph."""
        if not self._basename:
            return None
        return Glyph(self._basename, self.font)

    @property
    def rGlyph(self) -> RGlyph:
        """FontParts RGlyph object."""
        return self.font.rFont[self.name]

    @property
    def range(self) -> Range:
        """Range object."""
        if self.isOptional and not(self.isSet or self.isSalt):
            return None
        ranges = Request(CONFIG['smufl.urls']['rangesJson'],
                         CONFIG['smufl.paths']['rangesJson']).json()
        return Range(self, ranges)

    @property
    def suffix(self) -> str | None:
        """Return suffix of alternates."""
        if not (self.isSalt or self.isSet):
            return None
        return self.name.split('.')[1]

    @property
    def _basename(self) -> str | None:
        # Name of base glyph.
        _basename = self.name[:7]
        return _basename if _basename in self.font.rFont else None
