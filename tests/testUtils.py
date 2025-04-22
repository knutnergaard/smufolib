import contextlib
import json
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from smufolib.utils import converters


def generateGlyph(font, name, **kwargs):
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
    @contextmanager
    def assertNotRaises(self, exc_type):
        try:
            yield None
        except exc_type:
            raise self.failureException("{} raised".format(exc_type.__name__))
