"""Generate CSV table of engraving defaults mapping for SMufoLib documentaton.

The script generates a CSV table reflecting the mapping of attributes to glyph names
and ruler functions defined in :data:`.EngravingDefaults.ENGRAVING_DEFAULTS_MAPPING`.

"""

import csv
from pathlib import Path

from smufolib.utils import converters, rulers


def main():
    """Main function of the script."""

    # pylint: disable=C0103

    filePath = Path(__file__).parents[2] / "docs" / "engraving_defaults_mapping.csv"

    with open(filePath, "w", encoding="utf-8", newline="") as csvfile:
        fieldnames = ["Attribute", "Glyph", "Ruler Function"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

        writer.writeheader()

        for attributeName, mapping in rulers.ENGRAVING_DEFAULTS_MAPPING.items():
            if attributeName == "textFontFamily":
                writer.writerow(
                    {
                        "Attribute": f":attr:`.{attributeName}`",
                        "Glyph": "",
                        "Ruler Function": "",
                    }
                )
            else:
                rulerName = mapping["ruler"]
                glyphName = mapping["glyph"]
                decimal = converters.toDecimal(glyphName)
                uniHex = converters.toUniHex(decimal)
                writer.writerow(
                    {
                        "Attribute": f":attr:`.{attributeName}`",
                        "Glyph": uniHex,
                        "Ruler Function": f":func:`~.rulers.{rulerName}`",
                    }
                )


if __name__ == "__main__":
    main()
