from __future__ import annotations
from typing import Any
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import json

from smufolib import config, converters
from smufolib.objects.font import Font
from smufolib.request import Request

CONFIG = config.load()

# pylint: disable=invalid-name, unused-argument, too-many-branches


#: Available arguments and their settings.
CLI_ARGUMENTS: dict[str, dict[str, Any]] = {
    'attributes': {
        'nargs': '+',
        'help': "attribute names to include in processing"
    },
    'classesData': {
        'type': Request,
        'help': "path to classes metadata file"
    },
    'clear': {
        'action': 'store_true',
        'help': "erase preexisting objects on execution"
    },
    'color': {
        'nargs': 4,
        'type': converters.toNumber,
        'help': "list of RGBA color values"
    },
    'colors': {
        'type': json.loads,
        'help': "keys mapped to RGBA color arrays as JSON string"
    },
    'exclude': {
        'nargs': '+',
        'help': "objects to exclude from processing"
    },
    'font': {
        'type': Font,
        'help': "path to UFO file"
    },
    'fontData': {
        'type': Request,
        'help': "path to font metadata file"
    },
    'glyphnamesData': {
        'type': Request,
        'help': "path to glyphnames metadata file"
    },
    'include': {
        'nargs': '+',
        'help': "objects to include in processing"
    },
    'includeOptionals': {
        'action': 'store_true',
        'help': "include optional glyphs"
    },
    'mark': {
        'action': 'store_true',
        'help': "apply defined color values to objects"
    },
    'overwrite': {
        'action': 'store_true',
        'help': "overwrite preexisting values"
    },
    'rangesData': {
        'type': Request,
        'help': "path to ranges metadata file"
    },
    'sourcePath': {
        'type': Request,
        'help': "path to source file or directory"
    },
    'spaces': {
        'action': 'store_true',
        'help': "set unit of measurement to staff spaces"
    },
    'targetPath': {
        'help': "path to target file or directory"
    },
    'verbose': {
        'action': 'store_true',
        'help': "make output verbose"
    }
}


def commonParser(*args, addHelp: bool = False, description: str | None = None,
                 customHelpers: dict[str] = None, **kwargs) -> ArgumentParser:
    r"""Provide generic command-line arguments and options.

    See the :ref:`Available Options` for details.

    :param \*args: Required positional arguments to assign.
    :param addHelp: Add help message. Should be :obj:`False` when
        function is parent and otherwise :obj:`True`. Defaults to False.
    :param description: Program description when used directly. Defaults
        to :obj:`None`
    :param customHelpers: arguments mapped to custom help strings to
        override the default. Defaults to :obj:`None`
    :param \**kwargs: Options and their default values to assign.
    :raises TypeError: Duplicate arguments in \*args and \**kwargs.

    Examples::

        >>> import argparse
        >>> from smufolib import Font, cli
        >>> args = cli.commonParser('font', clear=True)
        >>> parser = argparse.ArgumentParser(parents=[args],
        ...             description='showcase commonParser')
        >>> parser.add_argument(
        ...     '-O', '--include-optionals',
        ...     action='store_true',
        ...     default=includeOptionals,
        ...     help="include optional glyphs",
        ...     dest='includeOptionals'
        ... )
        >>> parser.parse_args("-h".split()))
        usage: test.py [-h] [-x] [-O] font

        showcase commonParser

        positional arguments:
            font         path to UFO file

        optional arguments:
            -h, --help                show this help message and exit
            -x, --clear               erase preexisting objects on execution
            -O, --include-optionals   include optional glyphs

    ::

        >>> parser.parse_args("-f path/to/my/font.ufo".split())
        Namespace(font=<Font 'MyFont' path='path/to/my/font.ufo' at 4377107232>, mark=False)

    ::

        >>> parser.parse_args("-f path/to/my/font.ufo --clear".split())
        Namespace(font=<Font 'MyFont' path='path/to/my/font.ufo' at 4377107232>, mark=True)

    """

    parser = ArgumentParser(add_help=addHelp,
                            formatter_class=ArgumentDefaultsHelpFormatter,
                            description=description)

    for arg in args:
        CLI_ARGUMENTS[arg]['metavar'] = converters.toKebab(arg)
        parser.add_argument(arg, **CLI_ARGUMENTS[arg])

    seen = set()
    for key, value in kwargs.items():
        if key in args:
            raise TypeError(
                f"Option '{key}' is already added as positional argument.")

        flags = _generateFlags(key)
        assert flags[0] not in seen, f"Short flag '{flags[0]}' is duplicate."
        seen.add(flags[0])

        CLI_ARGUMENTS[key]['dest'] = key
        if value is not None:
            CLI_ARGUMENTS[key]['default'] = value
        parser.add_argument(*flags, **CLI_ARGUMENTS[key])
    return parser


def _generateFlags(argument):
    # Generates tuple of option flags.
    shortFlags = CONFIG['cli.shortFlags']
    longFlag = f'--{converters.toKebab(argument)}'
    return (shortFlags[argument], longFlag)
