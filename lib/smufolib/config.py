"""
Configuration parser module for SMufoLib.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple
import argparse
import errno
import os
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path

from smufolib import converters
if TYPE_CHECKING:
    from smufolib.font import Font


# pylint: disable=invalid-name

# optional specific filepath of smufolib.cfg
INI_FILEPATH = ''


def configLoad(filepath=INI_FILEPATH):
    """
    Reformats and parses config.ini

    :param filepath: pathname to config.ini.
    """
    config = _readConfig(filepath)
    parsed = {}
    for section in config.sections():

        if section == 'Engraving Defaults':
            camel_section = converters.toCamelCase(section)
            options = _parseEngravingDefaults(config, section)
            parsed[camel_section] = options

        elif section == 'Mark Color':
            camel_section = converters.toCamelCase(section)
            options = _parseColor(config, section)
            parsed[camel_section] = options

        else:
            options = {}
            camel_section = converters.toCamelCase(section)
            for option, value in config[section].items():
                camel_option = converters.toCamelCase(option)
                value = _parseConfigValue(config, section, option)
                options[camel_option] = value
                parsed[camel_section] = options

    return parsed


def setDefaultPath(font: Font, stem: str):
    """
    Sets filepath to directory/generic_filename.json.
    Directory defaults to cwd if not specified.

    :param stem: last, function-specific part of filename.
    :param font: the font from which to extract name.
    """
    config = configLoad()
    directory = config['fontPaths']['directory']
    if not directory:
        directory = Path(__file__).parent
    filename = Path(f'{font.name.lower().replace(" ", "_")}_{stem}')
    return directory / filename


def _readConfig(filepath):
    config = ConfigParser(interpolation=ExtendedInterpolation())
    if not filepath:
        for location in (Path.home(), os.getenv('SMUFOLIB_CFG'), Path.cwd()):
            try:
                with open(os.path.join(location, 'smufolib.cfg'),
                          encoding='utf') as source:
                    config.read_file(source)
                    break
            except (FileNotFoundError, TypeError):
                continue
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT))

    return config


def _parseEngravingDefaults(config: ConfigParser,
                            section: str='Engraving Defaults'
                            ) -> Dict[str, float | int]:
    """
    Format keys and values of engraving defaults.

    :param config: ConfigParser object.
    :param section: engraving defaults section.
    """
    engravingDefaults = {}
    for option, value in config[section].items():
        if not value:
            continue

        value = _parseConfigValue(config, section, option)
        option = converters.toCamelCase(option)
        engravingDefaults[option] = value
    return engravingDefaults


def _parseColor(config: ConfigParser,
                section: str = 'Mark Color'
                ) -> Tuple[int | float] | None:
    """
    Parse Mark Color section independently of value order in config.

    :param config: ConfigParser object.
    :param section: mark color section.
    """
    colors = ('red', 'green', 'blue', 'alpha')
    return tuple(_parseConfigValue(config, section, c) for c in colors)


def _parseConfigValue(config: ConfigParser, section: str, option: str
                      ) -> int | float | bool | Tuple[str] | str | None:
    """
    Parse configuration values.

    :param config: ConfigParser object.
    :param section: name of section.
    :param option: name of option.
    """
    try:
        return config.getint(section, option)
    except ValueError:
        try:
            return config.getfloat(section, option)
        except ValueError:
            try:
                return config.getboolean(section, option)
            except ValueError:
                string = config.get(section, option)
                if any((c in {')', ']'}) for c in string):
                    return tuple(string.strip(')][(').split(', '))
                return string if string else None
