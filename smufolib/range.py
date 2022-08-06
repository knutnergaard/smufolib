"""Range metadata module for SMufoLib."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Tuple

if TYPE_CHECKING:
    from smufolib.glyph import Glyph


class Range:
    """Class of SMuFL range-related metadata.

    :param glyph: parent glyph object.
    :param ranges: ranges.json source file.
    """

    # pylint: disable=invalid-name

    def __init__(self,
                 glyph: Glyph | None = None,
                 ranges: Dict[str, Dict[str, str | List[str]]] | None = None
                 ) -> None:

        self._glyph = glyph
        self._ranges = ranges

    def _getRangeValue(self, value: str) -> str | List[str] | None:
        # Get metadata values from ranges.json.
        for rang, values in self._ranges.items():
            if self._smuflName not in values['glyphs']:
                continue
            if value == 'range_name':
                return rang
            return values[value]

    @property
    def name(self) -> str | None:
        """Return name of affiliated SMuFL range."""
        return self._getRangeValue('range_name')

    @property
    def description(self) -> str | None:
        """Return description of affiliated SMuFL range."""
        return self._getRangeValue('description')

    @property
    def glyphs(self) -> Tuple[str]:
        """Glyph members of affiliated SMuFL range by canonical name."""
        return tuple(self._getRangeValue('glyphs'))

    @property
    def start(self) -> str | None:
        """Return start codepoint of affiliated SMuFL range."""
        return self._getRangeValue('range_start')

    @property
    def end(self) -> str | None:
        """Return end codepoint of affiliated SMuFL range."""
        return self._getRangeValue('range_end')

    @property
    def _smuflName(self) -> str | None:
        # SMuFL-specific canonical glyph name.
        if not self._glyph:
            return None
        if self._glyph.base.smuflName:
            return self._glyph.base.smuflName
        return self._glyph.smuflName
