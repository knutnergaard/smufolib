from unittest.mock import PropertyMock
from smufolib import Font
from smufolib import converters
from tests.testUtils import generateGlyph

font = Font()
type(font).path = PropertyMock(return_value="/path/to/MyFont.ufo")
font.info.familyName = "MyFont"
font.info.styleName = "Regular"
font.info.unitsPerEm = 1000

font.smufl.spaces = False
if font.smufl.engravingDefaults:
    font.smufl.engravingDefaults.arrowShaftThickness = 46
    font.smufl.engravingDefaults.barlineSeparation = 72

otherFont = Font()
if otherFont.smufl.engravingDefaults:
    otherFont.smufl.engravingDefaults.arrowShaftThickness = 52
    otherFont.smufl.engravingDefaults.barlineSeparation = 75


generateGlyph(
    font,
    "uniE050",
    smuflName="gClef",
    unicode=0xE050,
    width=230.5,
    points=((0, -634), (648, -634), (648, 1167), (0, 1167)),
)
generateGlyph(font, "uniEAA0", smuflName="wiggleTrillFastest")
generateGlyph(font, "uniE610", smuflName="stringsDownBow")
generateGlyph(
    font,
    "uniE260",
    smuflName="accidentalFlat",
    classes=(
        "accidentals",
        "accidentalsSagittalMixed",
        "accidentalsStandard",
        "combiningStaffPositions",
    ),
)
generateGlyph(
    font, "uniE266", smuflName="accidentalTripleFlat", classes=["accidentalsStandard"]
)
generateGlyph(
    font, "uniE267", smuflName="accidentalNaturalFlat", classes=["accidentalsStandard"]
)
generateGlyph(
    font,
    "uniE240",
    anchors=(
        ("graceNoteSlashNE", (321, -199)),
        ("graceNoteSlashSW", (-161, -614)),
        ("stemUpNW", (0, -10)),
    ),
)
generateGlyph(font, "uniE26A_uniE260_uniE26B")
generateGlyph(font, "uniE26A", smuflName="accidentalParensLeft")
generateGlyph(font, "uniE26B", smuflName="accidentalParensRight")
generateGlyph(font, "uniE050.ss01", unicode=0xF472, smuflName="gClefSmall")
generateGlyph(font, "uniE062", smuflName="fClef")
generateGlyph(font, "uniE062.salt01", smuflName="fClefFrench")
generateGlyph(font, "uniE07F", smuflName="clefChangeCombining")
generateGlyph(font, "space")
