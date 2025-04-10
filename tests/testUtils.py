import contextlib
import json
from io import StringIO
from tempfile import TemporaryDirectory
from pathlib import Path

from smufolib import converters


def generateGlyph(font, name, unicode=None, smuflName=None):
    glyph = font.newGlyph(name)
    if unicode:
        glyph.unicode = unicode
    if smuflName:
        glyph.smufl.name = smuflName
    return glyph


def generateLigatureComponents(ligature):
    glyphs = []
    font = ligature.font
    for i, componentName in enumerate(ligature.name.split("_")):
        glyph = font.newGlyph(componentName)
        glyph.unicode = converters.toDecimal(componentName)
        glyph.lib["com.smufolib.name"] = f"smuflName{i}"
        glyphs.append(glyph)
    return tuple(glyphs)


def drawLines(glyph, points):
    pen = glyph.getPen()

    if not points:
        return glyph

    pen.moveTo(points[0])
    for point in points[1:]:
        pen.lineTo(point)
    pen.closePath()

    return glyph


def drawCurves(glyph, points):
    pen = glyph.getPen()

    if not points:
        return glyph

    pen.moveTo(points[0])
    for pointSet in points[1:]:
        pen.curveTo(*pointSet)
    pen.closePath()

    return glyph


def drawCircle(glyph, center, radius):
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

    return drawCurves(glyph, points)


def getVerboseOutput(function, *args, **kwargs):
    buffer = StringIO()
    with contextlib.redirect_stdout(buffer):
        function(*args, **kwargs)

    return buffer.getvalue()


class TempDirMixin:
    def setUp(self):
        super().setUp()
        self._tempDir = TemporaryDirectory()
        self.addCleanup(self._tempDir.cleanup)
        self.tempPath = Path(self._tempDir.name)


class SavedFontMixin(TempDirMixin):
    def saveFontToTemp(self, filename="test.ufo"):
        self.fontPath = self.tempPath / filename
        self.font.save(str(self.fontPath))
        return self.fontPath


class SavedMetadataMixin(TempDirMixin):
    def saveMetadataToTemp(self, filename="metadata.json"):
        self.metadataPath = self.tempPath / filename
        self.metadataPath.write_text(json.dumps(self.metadata))
        return self.metadataPath


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
