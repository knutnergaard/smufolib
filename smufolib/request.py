# pylint: disable=C0114
from __future__ import annotations
from typing import Any
import contextlib
from pathlib import Path
import json
import urllib.request
import warnings

from smufolib import config
from smufolib.normalizers import normalizeRequestPath

CONFIG = config.load()


class Request:
    """Send HTTP or filesystem request.

    A fallback path (e.g., a filesystem path to the same file), may be
    specified in case of connection failure
    (:class:`urllib.error.URLError`) if the primary path is a URL.

    An optional warning may be raised in the event of a fallback.

    :param path: Primary URL or filepath.
    :param fallback: Fallback filepath to use if path raises URLError.
    :param mode: File usage specification. See :func:`open` for details.
    :param encoding: File text encoding. See :func:`open` for details.
        Defaults to :ref:`[request]` ``encoding`` configuration.
    :param warn: Warn if URLError is raised before fallback request.
        Defaults to :ref:`[request]` ``warn`` configuration.

    """

    # pylint: disable=invalid-name, too-few-public-methods

    def __init__(self, path: Path | str | None = None,
                 fallback: Path | str | None = None,
                 mode: str = 'r',
                 encoding: str = CONFIG['request']['encoding'],
                 warn: bool = CONFIG['request']['warn']) -> None:
        self._path = path
        self._fallback = fallback
        self._mode = mode
        self._encoding = encoding
        self._warn = warn

    def __repr__(self):
        return (f"<{self.__class__.__name__} '{self.path}' "
                f"('{self.fallback}') at {id(self)}>")

    def json(self) -> dict[str, Any]:
        """Parse request as JSON."""
        if self.raw is None:
            return None
        return json.loads(self.raw)

    @property
    def raw(self) -> str | bytes:
        """Make a request and returns raw file contents."""
        if (self.path is None and self.fallback is None):
            raise ValueError(f"Path/fallback must be '{Path.__name__}' "
                             "or 'str' not 'NoneType'.")
        # Employ context manager stack for on- and offline use cases.
        with contextlib.ExitStack() as stack:
            try:
                raw = stack.enter_context(urllib.request.urlopen(self.path))
                return raw.read()
            except (urllib.error.URLError, AttributeError) as exc:
                if not self.fallback:
                    raise urllib.error.URLError(
                        f'Could not connect to url: {self.path}.') from exc

                if self._warn:
                    warnings.warn(
                        f"Could not connect to url: {self.path}.", URLWarning)
                raw = stack.enter_context(
                    open(self.fallback, self.mode, encoding=self.encoding))
                return raw.read()

            except ValueError:
                raw = stack.enter_context(
                    open(self.path, self.mode, encoding=self.encoding))
                return raw.read()

    @property
    def path(self) -> str | None:
        """Primary URL or filepath as string."""
        return normalizeRequestPath(self._path)

    @property
    def fallback(self) -> str | None:
        """Fallback URL or filepath as string."""
        return normalizeRequestPath(self._fallback)

    @property
    def mode(self) -> str:
        """File usage specification."""
        return self._mode

    @property
    def encoding(self) -> str:
        """File text encoding."""
        return self._encoding


class URLWarning(Warning):
    """URL connection failure warning."""
