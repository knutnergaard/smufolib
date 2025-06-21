"""Generate error templates CSV table for SMufoLib documentaton.

The script generates a table representation of :data:`.ERROR_TEMPLATES`
for documentation purposes.

"""

import csv
from pathlib import Path

from smufolib.utils import error

# pylint: disable=C0103


def main():
    """Main function of the script."""

    filePath = Path(__file__).parents[2] / "docs" / "error_templates.csv"

    with open(filePath, "w", encoding="utf-8", newline="") as csvfile:
        fieldnames = ["Key", "Template"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

        writer.writeheader()

        for key, template in error.ERROR_TEMPLATES.items():
            formattedKey = f'``"{key}"``'
            formattedTemplate = _replaceBracesWithBackticks(template).strip()
            writer.writerow({"Key": formattedKey, "Template": formattedTemplate})


def _replaceBracesWithBackticks(text: str) -> str:
    translationTable = str.maketrans("{}", "``")
    return text.translate(translationTable)


if __name__ == "__main__":
    main()
