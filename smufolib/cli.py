"""Command Line Interface for SMufoLib."""

from __future__ import annotations
from argparse import ArgumentParser, Namespace
from pathlib import Path

from smufolib import Font, Request

# pylint: disable=invalid-name, unused-argument, too-many-branches


def argParser(*args: str,
              addHelp: bool = False,
              description: str | None = None,
              **kwargs) -> Namespace:
    """Provide generic command line options to smufolib scripts.

    All arguments are optional and may be imported as needed to avoid
    having to define them in each individual script. Additional options
    may be defined on a script-by-script basis with `argParser` passed
    as a parent to the script's `ArgumentParser`.

    :param args: positional arguments for testing purposes.
    :param addHelp: add help message. Should be False when `argParser`
        is parent and otherwise True.
    :param description: program description used when used directly.
    :param kwargs: imported optional arguments and default values.
    """
    parser = ArgumentParser(add_help=addHelp, description=description)

    if 'clear' in kwargs:
        parser.add_argument(
            '-x', '--clear',
            action='store_true',
            default=kwargs['clear'],
            help="Erase preexisting objects on execution.")

    if 'color' in kwargs:
        parser.add_argument(
            '-c', '--color',
            action='store_true',
            default=kwargs['color'],
            help="Apply config defined color values.")

    if 'exclude' in kwargs:
        parser.add_argument(
            '-e', '--exclude',
            nargs='+',
            default=kwargs['exclude'],
            help="List of data points to exclude from processing.")

    if 'font' in kwargs:
        parser.add_argument(
            '-f', '--font',
            type=Font,
            default=kwargs['font'],
            help="Override default path to UFO file.")

    if 'include' in kwargs:
        parser.add_argument(
            '-i', '--include',
            nargs='+',
            default=kwargs['include'],
            help="List of data points to include in processing.")

    if 'mark' in kwargs:
        parser.add_argument(
            '-m', '--mark',
            action='store_true',
            default=kwargs['mark'],
            help="Mark processed glyphs with cofig defined color.")

    if 'classData' in kwargs:
        parser.add_argument(
            '-cd', '--class-data',
            type=Request,
            default=kwargs['classData'],
            help="Override default path to class metadata.",
            dest='classData')

    if 'fontData' in kwargs:
        parser.add_argument(
            '-fd', '--font-data',
            type=Request,
            default=kwargs['fontData'],
            help="Override default path to font metadata.",
            dest='fontData')

    if 'glyphnameData' in kwargs:
        parser.add_argument(
            '-gd', '--glyphname-data',
            type=Request,
            default=kwargs['glyphnameData'],
            help="Override default path to glyphname metadata.",
            dest='glyphnameData')

    if 'rangeData' in kwargs:
        parser.add_argument(
            '-rd', '--range-data',
            type=Request,
            default=kwargs['rangeData'],
            help="Override default path to range metadata.",
            dest='rangeData')

    if 'overwrite' in kwargs:
        parser.add_argument(
            '-w', '--overwrite',
            action='store_true',
            default=kwargs['overwrite'],
            help="Overwrite preexisting values.")

    if 'source' in kwargs:
        parser.add_argument(
            '-s', '--source',
            type=Path,
            default=kwargs['source'],
            help="Override default path to source file.")

    if 'target' in kwargs:
        parser.add_argument(
            '-t', '--target',
            type=Path,
            default=kwargs['target'],
            help="Override default path to target file.")

    return parser
