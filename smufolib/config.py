# pylint: disable=C0103, C0114
from __future__ import annotations
from typing import Any
import os
import importlib.resources
from urllib.parse import urlparse

from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path


def load(path: Path | str | None = None) -> dict[str, Any]:
    """Load parsed config file as :class:`dict`.

    If `path` is not provided, configuration is obtained by searching the standard
    locations described in the user guide (see :ref:`configuring-smufolib`). Files found
    later in the search order override earlier ones.

    If `path` is provided, only that file is loaded.

    :param path: Path to `smufolib.cfg`. Defaults to :obj:`None`.

    Example:

        >>> from smufolib import config
        >>> cfg = config.load()
        >>> cfg["request"]
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

    defaultPath = importlib.resources.files("smufolib").joinpath("defaults.cfg")
    with defaultPath.open("r", encoding="utf-8") as defaults:
        config.read_file(defaults)

    userPaths = _selectPaths(path)
    parentPaths = [Path(str(defaultPath)).parent] + [p.parent for p in userPaths]

    config.read(userPaths, encoding="utf-8")
    _resolveMetadataPaths(config, parentPaths)

    return config


def _selectPaths(path: Path | str | None) -> list[Path]:
    # Create a list of all possible filepaths in order of priority.
    nameExtension = ("smufolib", "cfg")
    envValue = os.getenv("_".join(nameExtension).upper())
    candidates = [
        Path.home() / ".".join(nameExtension),
        Path.cwd() / ".".join(nameExtension),
    ]

    if envValue:
        candidates.append(Path(envValue))

    if path:
        candidates.append(Path(path))

    return [p for p in candidates if Path(p).exists()]


def _parse(
    config: ConfigParser, section: str, option: str
) -> str | int | float | bool | tuple[str | float, ...] | None:
    # Parse configured values.
    stringValue = config.get(section, option)

    try:
        return config.getint(section, option)
    except ValueError:
        try:
            return config.getfloat(section, option)
        except ValueError:
            try:
                return config.getboolean(section, option)
            except ValueError:
                if any((c in {")", "]"}) for c in stringValue):
                    iterable = tuple(stringValue.strip(")][(").split(", "))
                    try:
                        return tuple(
                            float(i) if "." in i else int(i) if i.isdigit() else i
                            for i in iterable
                        )
                    except ValueError:
                        return iterable
                # Strip \n to perserve multiline option after setting
                # config.optionxform = str.
                return stringValue.replace("\n", "") if stringValue else None


def _resolveMetadataPaths(config: ConfigParser, baseDirs: list[Path]) -> None:
    # Resolve relative paths in [metadata] sections.
    for section in ("metadata.paths", "metadata.fallbacks"):
        if not config.has_section(section):
            continue

        for key, value in config.items(section):
            path = Path(value)

            if urlparse(value).scheme in {"http", "https"}:
                continue

            if path.is_absolute():
                continue

            for base in reversed(baseDirs):
                candidate = base / path
                if candidate.exists():
                    config.set(section, key, str(candidate.resolve()))
                    break
