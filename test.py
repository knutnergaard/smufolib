from fontParts.fontshell.component import RComponent
from fontParts.fontshell.contour import RContour
from tests import testEnvironment
from smufolib.objects.engravingDefaults import EngravingDefaults
from smufolib.objects.font import Font
from smufolib.objects.glyph import Glyph
from smufolib.objects.layer import Layer
from smufolib.objects.range import Range
from smufolib.objects.smufl import Smufl
from smufolib.request import Request


classMapping = {
    "component": RComponent,
    "contour": RContour,
    "engravingDefaults": EngravingDefaults,
    "font": Font,
    "glyph": Glyph,
    "layer": Layer,
    "range": Range,
    "smufl": Smufl,
    "request": Request,
}


def smufolibObjectGenerator(cls):
    unrequested = []
    obj = classMapping[cls]()
    return obj, unrequested


if __name__ == "__main__":
    import sys

    if {"-v", "--verbose"}.intersection(sys.argv):
        verbosity = 2
    else:
        verbosity = 1
    testEnvironment(smufolibObjectGenerator, verbosity=verbosity)
