"""
Request module for SMufoLib.
"""
from __future__ import annotations
from typing import Dict, Any
import contextlib
import json
import urllib.request
import warnings

import smufolib.error

# pylint: disable=invalid-name


class Request:
    """
    HTTP or filesystem request.

    A fallback to `path` (e.g., a filesystem path to the same file), may
    be specified in case of connection failure (URLError).

    An optional warning may be raised in the event of a fallback.

    :param path: URL or filepath to JSON.
    :param fallback: fallback value to use if path raises URLError.
    """

    def __init__(self, path, fallback=None):
        self.path = path
        self.fallback = fallback
        self._warn = True

    def json(self, warn: bool = True) -> Dict[str, Any]:
        """
        Parses request as JSON.

        :param warn: sets `Request.warn`.
        """
        self.warn = warn
        return json.loads(self._raw)

    @property
    def _raw(self) -> str | bytes:
        # Makes a request and returns raw response object.
        # Employs context manager stack for on- and offline use cases.
        with contextlib.ExitStack() as stack:
            try:
                raw = stack.enter_context(urllib.request.urlopen(self.path))
            except urllib.error.URLError:
                if self.warn:
                    warnings.warn(f"Could not connect to url: {self.path}.",
                        smufolib.error.URLWarning)
                raw = stack.enter_context(open(self.fallback,
                                               'r', encoding='utf8'))
            except ValueError:
                raw = stack.enter_context(open(self.path,
                                               'r', encoding='utf8'))
            return raw.read()

    @property
    def warn(self):
        """
        Warn if URLError is raised before fallback request.
        """
        return self._warn

    @warn.setter
    def warn(self, value):
        self._warn = value

from smufolib.config import configLoad
