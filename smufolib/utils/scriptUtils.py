from pathlib import Path
from typing import Any

from smufolib.objects.font import Font
from smufolib.request import Request
from smufolib.utils import error, normalizers


JsonDict = dict[str, Any]
ColorValue = int | float
ColorTuple = tuple[ColorValue, ColorValue, ColorValue, ColorValue]


def normalizeColor(color: ColorTuple | None, mark: bool) -> ColorTuple | None:
    """ "Ensure that `color` is valid based on the `mark` setting."

    If the input `color` is :obj:`None` and `mark` is :obj:`True`, a :class:`TypeError`
    is raised. Otherwise, the color is normalized using :func:`.normalizeColor`.


    :param color: The color value to normalize.
    :param mark: Mark objects with the specified `color`.
    :raises TypeError: If `color` is not the expected type.

    """
    # Normalize `color` value.
    if color is None:
        if mark:
            raise TypeError(
                error.generateTypeError(
                    value=color,
                    validTypes=tuple,
                    objectName="color",
                    dependencyInfo="'mark' is True",
                )
            )
        return None
    return normalizers.normalizeColor(color)


def normalizeFont(font: Font | Path | str) -> Font:
    """Ensure that `font` represents a font object.

    If `font` is a :class:`str` or :class:`~pathlib.Path`, it is treated as a path and
    passed to the :class:`.Font` constructor.

    :param font: The font to normalize.
    :raises TypeError: If `font` is not the expected type.

    """
    # Convert font path to object if necessary.
    error.validateType(font, (Font, Path, str), "font")
    if isinstance(font, Font):
        return font
    return Font(font)


def normalizeJsonDict(jsonDict: JsonDict | None) -> JsonDict:
    """Ensure that `jsonDict` is not :obj:`None`.

    :param jsonDict: The JSON dictionary to validate.
    :raises TypeError: If `jsonDict` is :obj:`None`.

    """
    # Ensure `jsonDict` is not None.
    if jsonDict is None:
        raise TypeError(error.generateTypeError(jsonDict, JsonDict, "JSON file"))
    return jsonDict


def normalizeRequest(request: Request | Path | str) -> Request:
    """Ensure that `request` represents a request object.

    If `request` is a :class:`str` or :class:`~pathlib.Path`, it is treated as a path
    and passed to the :class:`.Request` constructor.

    :param request: The request to normalize.
    :raises TypeError: If `request` is not the expected type.

    """
    # Convert request path to object if necessary.
    error.validateType(request, (Request, Path, str), "request")
    if isinstance(request, Request):
        return request
    return Request(request)


def normalizeTargetPath(targetPath: str | Path) -> str | Path:
    # Ensure targetPath exists.
    if not Path(targetPath).exists():
        raise FileNotFoundError(
            error.generateErrorMessage("fileNotFound", objectName="targetPath")
        )
    return targetPath
