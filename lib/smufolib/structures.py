"""Metadata structures for SMufoLib.

"""
TEMPLATE = {
    'fontName': None,
    'fontVersion': None,
    'engravingDefaults': {},
    'glyphAdvanceWidths': {},
    'glyphBBoxes': {},
    'glyphsWithAlternates': {},
    'glyphsWithAnchors': {},
    'ligatures': {},
    'optionalGlyphs': {},
    'sets': {}
}

SETS = {
    'ss01': {
        'description': 'Smaller optical size for small staves',
        'type': 'opticalVariantsSmall'
    },
    'ss02': {
        'description': 'Short flags (to avoid augmentation dots)',
        'type': 'flagsShort'
    },
    'ss03': {
        'description': 'Straight flags',
        'type': 'flagsStraight'
    },
    'ss04': {
        'description': 'Large time signatures',
        'type': 'timeSigsLarge'
    },
    'ss05': {
        'description': 'Noteheads at larger optical size',
        'type': 'noteheadsLarge'
    },
    'ss06': {
        'description': 'Tuplet numbers at a lighter weight',
        'type': 'tupletsLight'
    },
    'ss07': {
        'description': 'Smaller optical size for subscript and superscript placement',
        'type': 'chordSymbolsOpticalVariants'
    },
    'ss08': {
        'description': 'Oversized slash noteheads',
        'type': 'slashesOversized'
    },
    'ss09': {
        'description': 'Large, narrow time signatures',
        'type': 'timeSigsLargeNarrow'
    },
    'ss10': {
        'description': 'Accidentals for figured bass with longer stems',
        'type': 'figbassAccidentalsLongerStems'
    }
}
