# What's New
## Breaking Changes
- Removed property `Request.raw`. Use properties `text` and `content` instead.
- Renamed `referenceFont` option to `font` in metadata sections of `smufolib.cfg` to
  clarify.
- Renamed placeholder `dependencyInfo` to `context` in `error.ERROR_TEMPLATES`.
- Renamed function parameter `dependencyInfo` to `context` in `error.generateTypeError`.
- Renamed constant `rulers.MAPPING` to `rulers.ENGRAVING_DEFAULTS_ATTRIBUTES`.
- Updated `__all__` to include:
  - `ANCHOR_NAMES`
  - `CLI_ARGUMENTS`
  - `commonParser`
  - `config`
  - `converters`
  - `createHelpFormatter`
  - `EngravingDefaults`
  - `ENGRAVING_DEFAULTS_ATTRIBUTES`
  - `error`
  - `Font`
  - `FONT_ATTRIBUTES`
  - `Glyph`
  - `GLYPH_ATTRIBUTES`
  - `Layer`
  - `normalizers`
  - `Range`
  - `Request`
  - `Smufl`
  - `rulers`
  - `stdUtils`
  - `scriptUtils`
  - `writeJson` 
  - This may cause `AttributeError` in code relying on previously accessible symbols.

## New Features
- Added `Request` class methods  `classes`, `glyphnames`, `ranges` and `font` for quick
  retrieval of standard metadata files.
- Added properties `text` and `content` to `Request` for accessing string or bytes
  responses respectively.
- Added properties `alternateGlyphs` and `alternateNames` to `Smufl` to retrieve
  alternates of a base glyph, similarly to existing ligature component methods.
- Added method `classMembers` to `Smufl` to retrieve all glyph members of a specified
  SMuFL class.
- Added support for wrapped object initialization to `Font`.
- Added parameter and property `auto` to `EngravingDefaults` to make enabling/disabling
  automatic calculations more flexible.
- Added User Guide to documentation.
- Added `error.ERROR_TEMPLATES`: 
  - `contextualAttributeError`
  - `contextualSetAttributeError`
  - `deprecated`
  - `deprecatedReplacement`
- Added `string` parameter to `error.generateErrorMessage` to facilitate user-defined
- Added bracketed canonical SMuFL glyph name (if present) to `Glyph.__repr__`.
  additional substring in error messages.
- Added doctests to ensure validity of documented code examples

## Deprecations
- Removed deprecated:
  - module `pointUtils`
  - property `Request.mode`
  - property `Smufl.range`

## Other Changes
- `error.ERROR_TEMPLATES`: 
    - Applied !r conversion in placeholders to improve clarity of argument values.
    - Removed trailing periods from templates for compatability with builtin fuzzy
      suggestions in Python 3.10.
- Added glyph access requirement to glyph-specific `Smufl` attributes to clarify usage
  intent.
    - Attempting to access these attributes from the font level now raises
      `AttributeError` instead of returning `None`.
- Refactored `EngravingDefaults` properties to be generated dynamically at runtime, to
  avoid unnecessary duplication.
- Rebranded Command Line Interface as CLI Framework to clarify intent and functionality.


