"""Generate CSV table of engraving defaults mapping for SMufoLib documentaton.

The script generates a CSV table reflecting the mapping of attributes to glyph names
and ruler functions defined in :data:`.EngravingDefaults.MAPPING`.

"""

import csv
import json
from pathlib import Path

from smufolib.utils import converters, rulers


def main():
    """Main function of the script."""

    # pylint: disable=C0103

    namesMapping = _buildNamesMapping()

    filePath = Path(__file__).parent.parent / "docs" / "mappings.csv"

    with open(filePath, "w", encoding="utf-8", newline="") as csvfile:
        fieldnames = ["Attribute", "Glyph", "Ruler Function"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

        writer.writeheader()

        for attributeName, mapping in rulers.MAPPING.items():
            if attributeName == "textFontFamily":
                writer.writerow(
                    {
                        "Attribute": f":attr:`.{attributeName}`",
                        "Glyph": "None",
                        "Ruler Function": "None",
                    }
                )
            else:
                rulerName = mapping["ruler"]
                glyphName = mapping["glyph"]
                smuflName = namesMapping[glyphName]
                writer.writerow(
                    {
                        "Attribute": f":attr:`.{attributeName}`",
                        "Glyph": f"`{glyphName} ({smuflName})`",
                        "Ruler Function": f":func:`~.rulers.{rulerName}`",
                    }
                )


def _buildNamesMapping():
    # Create an inverted glyph name mapping from glyphnames.json
    filepath = Path("../smufolib/smufolib/metadata/glyphnames.json").resolve()
    with filepath.open(encoding="utf-8") as jsonFile:
        metadata = json.load(jsonFile)
        return {converters.toUniName(v["codepoint"]): k for k, v in metadata.items()}


if __name__ == "__main__":
    main()
