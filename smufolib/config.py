"""Configuration module for SMufoLib."""
from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
import os
import errno
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path

if TYPE_CHECKING:
    from smufolib.font import Font


# pylint: disable=invalid-name

# optional specific filepath of smufolib.cfg
INI_FILEPATH = ''


def configLoad(filepath=INI_FILEPATH):
    """Reformats and parses config.ini.

    :param filepath: pathname to config.ini, defaults to INI_FILEPATH.
    """
    config = _readConfig(filepath)
    parsed = {}
    for section in config.sections():
        parsed[section] = {}
        for option, value in config[section].items():
            value = _parseConfigValue(config, section, option)
            parsed[section][option] = value

    return parsed


def setDefaultPath(font: Font, stem: str):
    """Set filepath to directory/generic_filename.json.

    Directory defaults to font's parent if not specified.

    :param stem: last, function-specific part of filename.
    :param font: the font from which to extract name.
    """
    config = configLoad()
    try:
        directory = config['fontPaths']['directory']
    except KeyError:
        directory = Path(font.path).parent
    filename = Path(f'{font.name.lower().replace(" ", "_")}_{stem}')
    return directory / filename


def _readConfig(filepath):
    # Read config file from multiple locations in order:
    # 1. Specified `filepath`.
    # 2. Home directory (User/username/)
    # 3. Environment variable SMUFOLIB_CFG
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.optionxform = str

    if not filepath:
        for location in (Path.home(),
                         os.getenv('SMUFOLIB_CFG')):
            try:
                with open(os.path.join(location, 'smufolib.cfg'),
                          encoding='utf-8') as source:
                    config.read_file(source)
                    break
            except (FileNotFoundError, TypeError):
                continue
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT))
    else:
        config.read(filepath)
    return config


def _parseConfigValue(config: ConfigParser, section: str, option: str
                      ) -> int | float | bool | Tuple[str] | str | None:
    # Parse configuration values.
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
                    iterable = tuple(string.strip(')][(').split(', '))
                    try:
                        return tuple(float(i) if '.' in i
                                     else int(i) for i in iterable)
                    except ValueError:
                        return iterable
                # Strip \n to perserve multiline option after setting
                # config.optionxform = str.
                return string.replace('\n', '') if string else None
