"""Generate error templates CSV table for SMufoLib documentaton.

The script generates a table representation of :const:`.ERROR_TEMPLATES`
for documentation purposes.

"""
import csv

from smufolib import error

# pylint: disable=C0103


def main():
    """Main function of the script."""

    with open('../docs/error_templates.csv', 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = ['Key', 'Template']
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

        writer.writeheader()

        for key, template in error.ERROR_TEMPLATES.items():
            formattedKey = f'``{key}``'
            formattedTemplate = _replaceBracesWithBackticks(template).strip()
            writer.writerow(
                {
                    'Key': formattedKey,
                    'Template': formattedTemplate
                }
            )


def _replaceBracesWithBackticks(text: str) -> str:
    translationTable = str.maketrans('{}', '``')
    return text.translate(translationTable)


if __name__ == '__main__':
    main()
