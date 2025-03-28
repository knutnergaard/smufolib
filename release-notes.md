# Breaking Changes ⚠️

Old font and glyph `lib` keys have been replaced with new keys to comply with the [reverse domain naming scheme](https://unifiedfontobject.org/versions/ufo3/conventions/#reverse-domain-naming-schemes)  recommended by the [UFO](http://unifiedfontobject.org/) specification.

## Migration Instructions

To migrate your data, run the provided migration script on a single `.ufo` file or a folder of multiple files in your terminal:
```bash
update-keys <path-to-file-or-folder>
```

The `importId` and `cleanFont` scripts have been adapted to the new naming scheme.

# New Features and Improvements

## General

- Added a property setter to `Range.smufl`.
- Changed parameter name `dependency` to `dependencyInfo`.
- Added digit check to secure parsing of integer tuples in `smufolib.cfg`
- Added a `round` parameter to `Smufl.toUnits`.

## Error Handling

- Updated the `spaces` attribute in `Smufl` and `EngravingDefaults` to raise an exception if the `font` or `font.info.unitsPerEm` attributes are `None` when the value is being set.
- Updated `EngravingDefaults` to disallow setting attributes if `font` is None.
- Remove automatic items and type checks in `error.validateType` to simplify and streamline the validation logic.
- Removed argument duplication check in `cli.commonParser` (to rely on `argparse.ArgumentError`)
- Added `"missingDependencyError"` to `error.ERROR_TEMPLATES` to handle cases where a dependency is missing.

## Code Quality

- Added a suite of tests encompassing the entire library and implemented coverage tracking
- Implemented linting and formatting with  [ruff](https://github.com/astral-sh/ruff).

# Bug Fixes

- `Smufl` and `EngravingDefaults` An exception is no longer raised when calling `__eq__` and `__hash__` on the `Smufl` or `EngravingDefaults` objects.
- Updated `Smufl.codepoint` to interact properly with `BaseGlyph.unicode`.
- Fixed an issue where Smufl.classes would return None instead of an empty tuple (`()`) when `Smufl.font` is not `None`.
- Fixed an issue with `engravingDefaults.update` not updating selected attributes correctly.
- Fixed and issue with lacking spaces between compound error messages.