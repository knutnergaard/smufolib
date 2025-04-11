# pylint: disable=C0103, C0114, R0913
from __future__ import annotations
from typing import Any
from pathlib import Path
import json
import urllib.request
import warnings

from smufolib import config
from smufolib.utils import error, normalizers

JsonDict = dict[str, Any]

CONFIG = config.load()


class Request:
    """Send HTTP or filesystem request.

    A fallback path (e.g., a filesystem path to the same file), may be
    specified in case of connection failure when the primary path is a
    URL.

    An optional warning may be raised in the event of a fallback.

    :param path: Primary URL or filepath.
    :param fallback: Fallback filepath to use if `path`
        raises :class:`urllib.error.URLError`.
    :param encoding: File text encoding. See :func:`open` for details.
        Defaults to :ref:`[request]` `encoding` configuration.
    :param warn: Warn if URLError is raised before fallback request.
        Defaults to :ref:`[request]` `warn` configuration.
    :param mode: File usage specification used with :attr:`raw`.
        See :func:`open` for details. Defaults to 'r' (read).

    """

    def __init__(
        self,
        path: Path | str | None = None,
        fallback: Path | str | None = None,
        mode: str = "r",
        encoding: str = CONFIG["request"]["encoding"],
        warn: bool = CONFIG["request"]["warn"],
    ) -> None:
        self._path = path
        self._fallback = fallback
        self._mode = mode
        self._encoding = encoding
        self._warn = warn

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} '{self.path}' "
            f"('{self.fallback}') at {id(self)}>"
        )

    def json(self) -> JsonDict | None:
        """Parse request as JSON.

        :raises json.JSONDecodeError: If the response cannot be parsed
            as JSON.
        :raises TypeError: If the raw data is None.

        """
        if self.raw is None:
            return None
        return json.loads(self.raw)

    @property
    def raw(self) -> str | bytes | None:
        """Make a request and return raw file contents.

        :raises ValueError: If both path and fallback are :obj:`None` or
            if the path or fallback file cannot be opened or read.
        :raises urllib.error.URLError: If there is an error with the URL
             request and no fallback is provided.
        :raises FileNotFoundError: If the specified file or fallback
            file cannot be found.

        """
        if self.path is None and self.fallback is None:
            return None

        try:
            if self.path is not None:
                return self._readFromURL()
            return self._readFromFallback()
        except ValueError:
            return self._readFromPath()

    def _readFromURL(self) -> bytes:
        # Read data from URL.
        if self.path is None:
            raise TypeError(
                error.generateTypeError(self.path, (str, Path, Request), "Request.path")
            )
        try:
            with urllib.request.urlopen(self.path) as raw:
                return raw.read()
        except urllib.error.URLError as exc:
            return self._handleURLError(exc)

    def _readFromFallback(self) -> bytes:
        # Read data from fallback file.
        if self.fallback is None:
            raise TypeError(
                error.generateTypeError(
                    self.fallback, (str, Path, Request), "Request.fallback"
                )
            )

        with open(self.fallback, self.mode, encoding=self.encoding) as raw:
            return raw.read()

    def _readFromPath(self) -> bytes:
        # Read data from path.
        if self.path is None:
            raise TypeError(
                error.generateTypeError(self.path, (str, Path, Request), "Request.path")
            )
        with open(self.path, self.mode, encoding=self.encoding) as raw:
            return raw.read()

    def _handleURLError(self, exc: urllib.error.URLError) -> bytes:
        # Handle URL error during online request.
        if not self.fallback:
            raise urllib.error.URLError(
                error.generateErrorMessage("urlError", url=self.path)
            ) from exc

        if self._warn:
            warnings.warn(
                error.generateErrorMessage("urlError", url=self.path), error.URLWarning
            )

        with open(self.fallback, self.mode, encoding=self.encoding) as fallback_file:
            return fallback_file.read()

    @property
    def path(self) -> str | None:
        """Primary URL or filepath as string.

        :raises TypeError: If the path cannot be normalized.

        """
        return normalizers.normalizeRequestPath(self._path, "path")

    @property
    def fallback(self) -> str | None:
        """Fallback URL or filepath as string.

        :raises TypeError: If the fallback path cannot be normalized.

        """
        return normalizers.normalizeRequestPath(self._fallback, "fallback")

    @property
    def mode(self) -> str:
        """File usage specification."""
        return self._mode

    @property
    def encoding(self) -> str:
        """File text encoding."""
        return self._encoding


def writeJson(
    filepath: Path | str,
    source: JsonDict,
    encoding: str = CONFIG["request"]["encoding"],
) -> None:
    """Writes JSON data to filepath.

    :param filepath: Path to target file.
    :param source: JSON data source.
    :param encoding: File text encoding. See :func:`open` for details.
        Defaults to :ref:`[request]` `encoding` configuration.
    :raises TypeError: If `filepath` is not the expected type.
    :raises ValueError: If there is an error serializing the JSON data
        or if `filepath` does not have a ``.json`` exctension.
    :raises FileNotFoundError: If the specified `filepath` cannot be found.
    :raises OSError: If there are any issues opening or writing to the file.
    :raises UnsupportedOperation: If the operation is not supported.

    """
    error.validateType(filepath, (Path, str), "filepath")
    if not str(filepath).endswith(".json"):
        raise ValueError(
            error.generateErrorMessage(
                "missingExtension", objectName="filepath", extension=".json"
            )
        )
    try:
        with open(filepath, "w", encoding=encoding) as outfile:
            json.dump(source, outfile, indent=4, sort_keys=False)
    except (TypeError, ValueError) as e:
        raise ValueError("serializationError") from e
