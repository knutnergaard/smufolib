import io
import contextlib

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


@contextlib.contextmanager
def suppressOutput():
    with (
        contextlib.redirect_stdout(io.StringIO()),
        contextlib.redirect_stderr(io.StringIO()),
    ):
        yield
