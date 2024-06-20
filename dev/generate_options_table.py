"""Generate options CSV table for SMufoLib documentaton."""

import csv
import json
from smufolib import Font, Request, cli, config, converters


CONFIG = config.load()
shortFlags = CONFIG['cli.shortFlags']

directives = {
    bool: ':class:`bool`',
    list: ':class:`list`',
    str: ':class:`str`',
    json.loads: ':func:`~json.loads`',
    Request: ':class:`~smufolib.request.Request`',
    Font:  ':class:`~smufolib.font.Font`',
    converters.toNumber: ':class:`list`'
}

with open('docs/options.csv', 'w', encoding='utf-8', newline='') as csvfile:
    fieldnames = ['Argument', 'Option', 'Type', 'Description']
    writer = csv.DictWriter(
        csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

    writer.writeheader()
    for name, settings in cli.CLI_ARGUMENTS.items():
        longFlag = converters.toKebab(name)
        optionType = settings.get('type', None)
        if not optionType:
            if settings.get('action', None) == 'store_true':
                optionType = directives[bool]
            elif 'nargs' in settings:
                optionType = directives[list]
            else:
                optionType = directives[str]
        else:
            optionType = directives[optionType]
        description = settings['help']
        writer.writerow(
            {
                'Argument': f'``{name}``',
                # Non-breaking spaces between flags necessary to avoid break in some cells.
                'Option': f'``--{longFlag}, {shortFlags[name]}``',
                'Type': optionType,
                # Add capital letter and period to help strings.
                'Description': f'{description[0].upper()}{description[1:]}.'
            }
        )
