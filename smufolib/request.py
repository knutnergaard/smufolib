"""Request module for SMufoLib."""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any
import contextlib
import json
import urllib.request
import warnings

import smufolib.error

if TYPE_CHECKING:
    from pathlib import Path


class Request:
    """HTTP or filesystem request.

    A fallback to `path` (e.g., a filesystem path to the same file), may
    be specified in case of connection failure (URLError).

    An optional warning may be raised in the event of a fallback.

    :param path: URL or filepath to JSON.
    :param fallback: fallback value to use if path raises URLError.
    :param warn: Warn if URLError is raised before fallback request.
    """

    # pylint: disable=invalid-name, too-few-public-methods

    def __init__(self, path: Path | str,
                 fallback: Path | str | None = None,
                 warn: bool = True) -> None:
        self.path = path
        self.fallback = fallback
        self.warn = warn

    def json(self) -> Dict[str, Any]:
        """Parse request as JSON."""
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
