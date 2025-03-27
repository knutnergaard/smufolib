# pylint: disable=C0103, C0114
from __future__ import annotations
from typing import Any
import os
import errno
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path


def load(path: Path | str | None = None) -> dict[str, Any]:
    """Load parsed config file as :class:`dict`.

    If the `path` parameter is an empty :class:`str` or :obj:`None`,
    the following locations are checked in order:

    #. Current working directory
    #. Home directory
    #. Environment variable :envvar:`SMUFOLIB_CFG`
    #. SMufoLib package directory

    :param path: Path to smufolib.cfg. Defaults to :obj:`None`.

    Example::

        >>> from smufolib import config
        >>> cfg = config.load()
        >>> cfg['request']
        {'encoding': 'utf-8', 'warn': True}

    """
    config = _readConfigFile(path)
    parsed: dict[str, Any] = {}
    for section in config.sections():
        parsed[section] = {}
        for option in config[section]:
            parsed[section][option] = _parse(config, section, option)
    return parsed


def _readConfigFile(path: Path | str | None) -> ConfigParser:
    # Read config file from selected filepath.
    config = ConfigParser(interpolation=ExtendedInterpolation())

    config.optionxform = str  # type: ignore

    with open(_selectPath(path), encoding="utf-8") as f:
        config.read_file(f)
    return config


def _selectPath(path: Path | str | None) -> str:
    # Select filepath to config file.
    if path and Path(path).exists():
        return str(path)

    nameExttension = ("smufolib", "cfg")
    for selection in (
        Path.cwd() / ".".join(nameExttension),
        Path.home() / ".".join(nameExttension),
        os.getenv("_".join(nameExttension).upper()),
        Path(__file__).parents[1] / "smufolib" / ".".join(nameExttension),
    ):
        if selection and Path(selection).exists():
            return str(selection)
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT))


def _parse(
    config: ConfigParser, section: str, option: str
) -> str | int | float | bool | tuple[str | float, ...] | None:
    # Parse configured values.
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
                if any((c in {")", "]"}) for c in string):
                    iterable = tuple(string.strip(")][(").split(", "))
                    try:
                        return tuple(
                            float(i) if "." in i else int(i) if i.isdigit() else i
                            for i in iterable
                        )
                    except ValueError:
                        return iterable
                # Strip \n to perserve multiline option after setting
                # config.optionxform = str.
                return string.replace("\n", "") if string else None
