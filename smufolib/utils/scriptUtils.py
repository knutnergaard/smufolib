"""Script utility functions.

This module provides a set of utility functions specifically intended for use in
scripts and applications. Particualarly, it provides a set of noramlizers to ensure the
integrity of objects frequently passed by the user in an application setting.

To import the module:

    >>> from smufolib import scriptUtils

"""

from pathlib import Path
from typing import Any

from smufolib.objects.font import Font
from smufolib.request import Request
from smufolib.utils import error, normalizers


JsonDict = dict[str, Any]
ColorValue = int | float
ColorTuple = tuple[ColorValue, ColorValue, ColorValue, ColorValue]
ColorDict = dict[str, ColorTuple]


def normalizeColor(color: ColorTuple | None, mark: bool) -> ColorTuple | None:
    """Ensure that `color` is valid based on the `mark` setting."

    If the input `color` is :obj:`None` and `mark` is :obj:`True`, a :class:`TypeError`
    is raised. Otherwise, the color is normalized
    each dictionary value

    :param color: The color value to normalize.
    :param mark: Mark objects with the specified `color`.
    :raises TypeError: If `color` is not the expected type.

    """
    if color is None:
        if mark:
            raise TypeError(
                error.generateTypeError(
                    value=color,
                    validTypes=tuple,
                    objectName="color",
                    context="'mark' is True",
                )
            )
        return None
    return normalizers.normalizeColor(color)


def normalizeColorDict(colorDict: ColorDict | None, mark: bool) -> ColorDict | None:
    """Ensure that `ColorDict` is valid based on the `mark` setting."

    If the input `ColorDict` is :obj:`None` and `mark` is :obj:`True`,
    a :class:`TypeError` is raised. Otherwise, each value is normalized
    using :func:`.normalizeColor`.


    :param colorDict: The color dictionary to normalize.
    :param mark: Mark objects with the specified colors in `colorDict`.
    :raises TypeError: If `colorDict` is not the expected type.

    """
    if colorDict is None:
        if mark:
            raise TypeError(
                error.generateTypeError(
                    value=colorDict,
                    validTypes=ColorDict,
                    objectName="colors",
                    context="'mark' is True",
                )
            )
        return None

    error.validateType(colorDict, dict, "colors")
    for value in colorDict.values():
        normalizers.normalizeColor(value)

    return colorDict


def normalizeFont(font: Font | Path | str) -> Font:
    """Ensure that `font` represents a font object.

    If `font` is a :class:`str` or :class:`~pathlib.Path`, it is treated as a path and
    passed to the :class:`.Font` constructor.

    :param font: The font to normalize.
    :raises TypeError: If `font` is not the expected type.

    """
    error.validateType(font, (Font, Path, str), "font")
    if isinstance(font, Font):
        return font
    return Font(font)


def normalizeJsonDict(jsonDict: JsonDict | None) -> JsonDict:
    """Ensure that `jsonDict` is not :obj:`None`.

    :param jsonDict: The JSON dictionary to validate.
    :raises TypeError: If `jsonDict` is :obj:`None`.

    """
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
    error.validateType(request, (Request, Path, str), "request")
    if isinstance(request, Request):
        return request
    return Request(request)


def normalizeTargetPath(targetPath: str | Path) -> Path:
    """Ensure that `targetPath` is an existing :class:`Path`.

    :param targetPath: The target path to normalize.
    :raises TypeError: If `targetPath` is not an expected type.
    :raises FileNotFoundError: If `targetPath` does not exist.

    """
    error.validateType(targetPath, (Path, str), "targetPath")
    targetPath = Path(targetPath)
    if not targetPath.exists():
        raise FileNotFoundError(
            error.generateErrorMessage("fileNotFound", objectName="targetPath")
        )
    return targetPath
