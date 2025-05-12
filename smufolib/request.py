# pylint: disable=C0103, C0114, R0913
from __future__ import annotations
from pathlib import Path
import json
import urllib.request
import warnings

from smufolib import config
from smufolib.utils import error, normalizers
from smufolib.utils._annotations import JsonDict

CONFIG = config.load()


class Request:
    """Send HTTP or filesystem request.

    A fallback path (e.g., a filesystem path to the same file), may be specified in case
    of connection failure when the primary path is a URL.

    An optional warning may be raised in the event of a fallback.

    :param path: Primary URL or filepath.
    :param fallback: Fallback filepath to use if `path` raises
        :class:`urllib.error.URLError`.
    :param encoding: File text encoding. See :func:`open` for details. Defaults to
        :ref:`[request]` `encoding` configuration.
    :param warn: Warn if URLError is raised before fallback request. Defaults to
        :ref:`[request]` `warn` configuration.
    :param mode: File usage specification used with :attr:`raw`. See :func:`open` for
        details. Defaults to 'r' (read).

    """

    @classmethod
    def classes(cls, decode: bool = True) -> JsonDict | str | None:
        """Retrieve `classes` metadata from configured paths.

        This method attempts to load metadata from the path specified in the `classes`
        option of the `[metadata.paths]` section in `smufolib.cfg`, falling back to
        `[metadata.fallbacks]` if necessary.

        :param decode: If :obj:`True`, return parsed JSON data; otherwise, return raw
            response. Defaults to :obj:`True`.

        """
        return cls._getMetadata("classes", decode=decode)

    @classmethod
    def glyphnames(cls, decode: bool = True) -> JsonDict | str | None:
        """Retrieve `glyphnanes` metadata from configured paths.

        This method attempts to load metadata from the path specified in the
        `glyphnanes` option of the `[metadata.paths]` section in `smufolib.cfg`, falling
        back to `[metadata.fallbacks]` if necessary.

        :param decode: If :obj:`True`, return parsed JSON data; otherwise, return raw
            response. Defaults to :obj:`True`.

        """
        return cls._getMetadata("glyphnames", decode=decode)

    @classmethod
    def ranges(cls, decode: bool = True) -> JsonDict | str | None:
        """Retrieve `ranges` metadata from configured paths.

        This method attempts to load metadata from the path specified in the `ranges`
        option of the `[metadata.paths]` section in `smufolib.cfg`, falling back to
        `[metadata.fallbacks]` if necessary.

        :param decode: If :obj:`True`, return parsed JSON data; otherwise, return raw
            response. Defaults to :obj:`True`.

        """
        return cls._getMetadata("ranges", decode=decode)

    @classmethod
    def font(cls, decode: bool = True) -> JsonDict | str | None:
        """Retrieve `font` metadata from configured paths.

        This method attempts to load metadata from the path specified in the `font`
        option of the `[metadata.paths]` section in `smufolib.cfg`, falling back to
        `[metadata.fallbacks]` if necessary.

        :param decode: If :obj:`True`, return parsed JSON data; otherwise, return raw
            response. Defaults to :obj:`True`.

        """
        return cls._getMetadata("font", decode=decode)

    @classmethod
    def _getMetadata(cls, filename: str, decode: bool = True) -> JsonDict | str | None:
        path = CONFIG["metadata.paths"][filename]
        fallback = CONFIG["metadata.fallbacks"][filename]
        request = cls(path, fallback)
        return request.json() if decode else request.text

    # TODO: Remove mode in 0.6

    def __init__(
        self,
        path: Path | str | None = None,
        fallback: Path | str | None = None,
        encoding: str = CONFIG["request"]["encoding"],
        warn: bool = CONFIG["request"]["warn"],
        mode: None = None,
    ) -> None:
        self._path = path
        self._fallback = fallback
        self._encoding = encoding
        self._warn = warn
        self._mode = mode

        if mode is not None:  # pragma: no cover
            warnings.warn(
                error.generateErrorMessage(
                    "deprecated", objectName="mode", version=0.5
                ),
                DeprecationWarning,
                stacklevel=2,
            )

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} '{self.path}' "
            f"('{self.fallback}') at {id(self)}>"
        )

    def json(self) -> JsonDict | None:
        """Parse request as JSON.

        :raises json.JSONDecodeError: If the response cannot be parsed as JSON.
        :raises TypeError: If the raw data is None.

        """
        if self.text is None:
            return None
        return json.loads(self.text)

    def _readPreferredSource(self) -> bytes | None:
        if self.path is None and self.fallback is None:
            return None

        try:
            return self._readFromURL()
        # TypeError guards against path being None
        except (urllib.error.URLError, TypeError):
            if self.fallback:
                return self._readFromFallback()
            raise
        # ValueError confirms that path is an assumed filepath (non-URL)
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

        with open(self.fallback, "rb") as raw:
            return raw.read()

    def _readFromPath(self) -> bytes:
        # Read data from path.
        if self.path is None:
            raise TypeError(
                error.generateTypeError(self.path, (str, Path, Request), "Request.path")
            )
        with open(self.path, "rb") as raw:
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

        with open(self.fallback, "rb") as fallback_file:
            return fallback_file.read()

    @property
    def path(self) -> str | None:
        """Primary URL or filepath as string.

        :raises TypeError: If the path cannot be normalized.

        """
        return normalizers.normalizeRequestPath(self._path, "path")

    @path.setter
    def path(self, value: Path | str | None) -> None:
        self._path = normalizers.normalizeRequestPath(value, "path")

    @property
    def fallback(self) -> str | None:
        """Fallback URL or filepath as string.

        :raises TypeError: If the fallback path cannot be normalized.

        """
        return normalizers.normalizeRequestPath(self._fallback, "fallback")

    @fallback.setter
    def fallback(self, value: str | None) -> None:
        self._fallback = normalizers.normalizeRequestPath(value, "fallback")

    @property
    def encoding(self) -> str:
        """File text encoding."""
        return self._encoding

    @encoding.setter
    def encoding(self, value: str):
        self._encoding = value

    @property
    def content(self) -> bytes | None:
        """The raw response data as bytes.

        This property is read-only.

        """
        return self._readPreferredSource()

    @property
    def text(self) -> str | None:
        """The raw response data as text.

        This property is read-only.

        """
        raw = self._readPreferredSource()
        if raw is None:
            return None
        return raw.decode(self.encoding)

    # TODO: Remove mode in v0.6.0

    @property
    def mode(self) -> None:
        """File usage specification.

        .. deprecated:: 0.5.1

        """
        warnings.warn(
            error.generateErrorMessage("deprecated", objectName="mode", version=0.5),
            DeprecationWarning,
            stacklevel=2,
        )
        return self._mode

    # TODO: Remove raw in v0.6.0

    @property
    def raw(self) -> bytes | None:
        """Make a request and return raw file contents.

        .. deprecated:: 0.5.1

            Use the :attr:`text` and :attr:`bytes` properties instead.


        :raises ValueError: If both path and fallback are :obj:`None` or if the path or
            fallback file cannot be opened or read.
        :raises urllib.error.URLError: If there is an error with the URL request and no
             fallback is provided.
        :raises FileNotFoundError: If the specified file or fallback file cannot be
            found.

        """
        warnings.warn(
            error.generateErrorMessage(
                "deprecated",
                string="Use 'content' or 'text' instead.",
                objectName="raw",
                version=0.5,
            ),
            DeprecationWarning,
            stacklevel=2,
        )

        if self.path is None and self.fallback is None:
            return None

        try:
            if self.path is not None:
                return self._readFromURL()
            return self._readFromFallback()
        except ValueError:
            return self._readFromPath()


def writeJson(
    filepath: Path | str,
    source: JsonDict,
    encoding: str = CONFIG["request"]["encoding"],
) -> None:
    """Writes JSON data to filepath.

    :param filepath: Path to target file.
    :param source: JSON data source.
    :param encoding: File text encoding. See :func:`open` for details. Defaults to
        :ref:`[request]` `encoding` configuration.
    :raises TypeError: If `filepath` is not the expected type.
    :raises ValueError: If there is an error serializing the JSON data or if `filepath`
        does not have a ``.json`` exctension.
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
