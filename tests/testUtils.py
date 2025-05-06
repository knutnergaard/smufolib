from __future__ import annotations
import contextlib
import json
import unittest
from collections.abc import Callable
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any

from smufolib.utils import converters
from smufolib.utils._annotations import CollectionType, PairType

if TYPE_CHECKING:
    from smufolib.objects.font import Font
    from smufolib.objects.glyph import Glyph


def generateGlyph(font: Font, name: str, **kwargs: Any) -> Glyph:
    glyph = font.newGlyph(name)
    glyph.unicode = kwargs.get("unicode")
    for attr, value in kwargs.items():
        if value is None:
            continue
        if attr == "points":
            drawLines(glyph, value)
        elif attr == "anchors":
            for anchorName, position in value:
                glyph.appendAnchor(anchorName, position)
        elif attr == "smuflName":
            (setattr(glyph.smufl, "name", value))
        elif attr in {"description", "classes", "codepoint"}:
            (setattr(glyph.smufl, attr, value))
        else:
            setattr(glyph, attr, value)
    return glyph


def generateLigatureComponents(ligature: Glyph) -> tuple[Glyph, ...]:
    glyphs = []
    font = ligature.font
    for i, componentName in enumerate(ligature.name.split("_")):
        glyph = font.newGlyph(componentName)
        glyph.unicode = converters.toDecimal(componentName)
        glyph.lib["com.smufolib.name"] = f"smuflName{i}"
        glyphs.append(glyph)
    return tuple(glyphs)


def drawLines(glyph, points: CollectionType[PairType[int | float]]) -> None:
    pen = glyph.getPen()

    if not points:
        return

    first, *rest = points
    pen.moveTo(first)
    for point in rest:
        pen.lineTo(point)
    pen.closePath()


def drawCurves(
    glyph: Glyph,
    points: CollectionType[
        PairType[int | float] | CollectionType[PairType[int | float]]
    ],
) -> None:
    pen = glyph.getPen()

    if not points:
        return

    first, *rest = points
    pen.moveTo(first)
    for pointSet in rest:
        pen.curveTo(*pointSet)
    pen.closePath()


def drawCircle(
    glyph: Glyph, center: PairType[int | float], radius: int | float
) -> None:
    k = 0.552284749831

    cx, cy = center
    r = radius
    points = (
        (cx, cy + r),
        ((cx + k * r, cy + r), (cx + r, cy + k * r), (cx + r, cy)),
        ((cx + r, cy - k * r), (cx + k * r, cy - r), (cx, cy - r)),
        ((cx - k * r, cy - r), (cx - r, cy - k * r), (cx - r, cy)),
        ((cx - r, cy + k * r), (cx - k * r, cy + r), (cx, cy + r)),
    )

    drawCurves(glyph, points)


def getVerboseOutput(function: Callable, *args: Any, **kwargs: Any) -> str:
    buffer = StringIO()
    with contextlib.redirect_stdout(buffer):
        function(*args, **kwargs)

    return buffer.getvalue()


class TempDirMixin(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._tempDir = TemporaryDirectory()
        self.addCleanup(self._tempDir.cleanup)
        self.tempPath = Path(self._tempDir.name)


class SavedFontMixin(TempDirMixin):
    def saveFontToTemp(self, filename="test.ufo"):
        fontPath = self.tempPath / filename
        self.font.save(str(fontPath))
        return fontPath


class SavedMetadataMixin(TempDirMixin):
    def saveMetadataToTemp(self, metadata=None, filename="metadata.json"):
        metadataToSave = metadata if metadata else self.metadata
        metadataPath = self.tempPath / filename
        metadataPath.write_text(json.dumps(metadataToSave))
        return metadataPath


class SavedConfigMixin(TempDirMixin):
    def saveConfigToTemp(self, config=None, filename="metadata.json"):
        configToSave = config if config else self.config
        configPath = self.tempPath / filename
        configPath.write_text(configToSave.strip(), encoding="utf-8")
        return configPath


class SuppressOutputMixin:
    def suppressOutput(self):
        self._suppress = self.redirectOutput()
        self._suppress.__enter__()
        self.addCleanup(self._suppress.__exit__, None, None, None)

    @staticmethod
    @contextlib.contextmanager
    def redirectOutput():
        with (
            contextlib.redirect_stdout(StringIO()),
            contextlib.redirect_stderr(StringIO()),
        ):
            yield


class AssertNotRaisesMixin:
    @contextlib.contextmanager
    def assertNotRaises(self, exc_type):
        try:
            yield None
        except exc_type:
            # pylint: disable-next=W0707
            raise self.failureException(f"{exc_type.__name__} raised")
