# pylint: disable=C0114
from __future__ import annotations
from typing import Any
from copy import deepcopy
from argparse import (
    ArgumentParser,
    HelpFormatter,
    RawDescriptionHelpFormatter,
    RawTextHelpFormatter,
    ArgumentDefaultsHelpFormatter,
    MetavarTypeHelpFormatter,
)
import json

from smufolib import config
from smufolib.objects.font import Font
from smufolib.request import Request
from smufolib.utils import converters, error

CONFIG = config.load()

# pylint: disable=C0103
# fmt: off

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

# fmt: on


def commonParser(
    *args: str,
    addHelp: bool = True,
    description: str | None = None,
    customHelpers: dict[str, str] | None = None,
    **kwargs: Any,
) -> ArgumentParser:
    r"""Provide generic command-line arguments and options.

    See the :ref:`Available Options` for details.

    :param \*args: Required positional arguments to assign.
    :param addHelp: Add help message. Should be :obj:`False` when
        function is parent and otherwise :obj:`True`. Defaults
        to :obj:`True`.
    :param description: Program description when used directly. Defaults
        to :obj:`None`
    :param customHelpers: Arguments mapped to custom help strings to
        override the default. Defaults to :obj:`None`
    :param \**kwargs: Options and their default values to assign.

    Examples::

        >>> import argparse
        >>> from smufolib import Font, cli
        >>> args = cli.commonParser('font', clear=True, addHelp=False)
        >>> parser = argparse.ArgumentParser(parents=[args],
        ...             description='showcase commonParser')
        >>> parser.add_argument(
        ...     '-O', '--include-optionals',
        ...     action='store_true',
        ...     help="include optional glyphs",
        ...     dest='includeOptionals'
        ... )
        >>> parser.parse_args("-h".split()))
        usage: test.py [-h] [-x] [-O] font

        Showcase commonParser.

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

    parser = ArgumentParser(add_help=addHelp, description=description)
    localArguments = deepcopy(CLI_ARGUMENTS)

    def addArgument(
        arg: str, flags: tuple[str, ...], customHelpers: dict[str, str] | None
    ) -> None:
        # Add argument to parser.
        if customHelpers and arg in customHelpers:
            localArguments[arg]["help"] = customHelpers[arg]
        parser.add_argument(*flags, **localArguments[arg])

    def generateFlags(argument: str) -> tuple[str, str]:
        # Generates tuple of option flags.
        shortFlags = CONFIG["cli.shortFlags"]
        longFlag = f"--{converters.toKebab(argument)}"
        return (shortFlags[argument], longFlag)

    for arg in args:
        flags: tuple[str, ...] = generateFlags(arg)
        if localArguments[arg].get("action") != "store_true":
            flags = (arg,)
            localArguments[arg]["metavar"] = converters.toKebab(arg)
        addArgument(arg, flags, customHelpers)

    for key, value in kwargs.items():
        if key in args:
            raise ValueError(error.generateErrorMessage("argumentConflict", key=key))

        flags = generateFlags(key)
        localArguments[key]["dest"] = key
        if value is not None:
            localArguments[key]["default"] = value
        addArgument(key, flags, customHelpers)

    return parser


def createHelpFormatter(formatters: str | tuple[str, ...]) -> type[HelpFormatter]:
    """Create child class of multiple help formatters.

    The returned :class:`HelpFormatter` class can be passed to the
    `formatter_class` parameter of :class:`argparse.ArgumentParser` to
    combine different formatters, despite the parameter only taking a
    single class as argument.

    :param formatters: Name of the formatter class or tuple of class
        names to be enabled as :class:`str` corresponding to
        either :class:`~argparse.RawDescriptionHelpFormatter`,
        :class:`~argparse.RawTextHelpFormatter`,
        :class:`~argparse.ArgumentDefaultsHelpFormatter`,
        :class:`~argparse.RawDescriptionHelpFormatter` or
        :class:`~argparse.MetavarTypeHelpFormatter`, or a :class:`tuple`
        of class names.
    :raises TypeError: If `formatters` is not an accepted type.
    :raises ValueError: If any `formatters` item is not recognised.

    """

    baseFormatters = {
        "HelpFormatter": HelpFormatter,
        "RawDescriptionHelpFormatter": RawDescriptionHelpFormatter,
        "RawTextHelpFormatter": RawTextHelpFormatter,
        "ArgumentDefaultsHelpFormatter": ArgumentDefaultsHelpFormatter,
        "MetavarTypeHelpFormatter": MetavarTypeHelpFormatter,
    }

    error.validateType(formatters, (str, tuple), "formatters")
    if isinstance(formatters, str):
        formatters = (formatters,)

    try:
        employed = tuple(baseFormatters[v] for v in formatters)
    except KeyError as exc:
        raise ValueError(
            error.suggestValue(
                # Casting exc to str to please mypy.
                str(exc),
                list(baseFormatters),
                "formatters",
                items=True,
            )
        ) from exc

    return type("HelpFormatter", employed, {})
