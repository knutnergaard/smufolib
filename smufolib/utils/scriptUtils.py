from pathlib import Path
from typing import Any

from smufolib.objects.font import Font
from smufolib.request import Request
from smufolib.utils import error, normalizers


JsonDict = dict[str, Any]
ColorValue = int | float
ColorTuple = tuple[ColorValue, ColorValue, ColorValue, ColorValue]


def normalizeColor(color: ColorTuple | None, mark: bool) -> ColorTuple | None:
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
    # Convert font path to object if necessary.
    error.validateType(font, (Font, Path, str), "font")
    if isinstance(font, Font):
        return font
    return Font(font)


def normalizeJsonDict(jsonDict: JsonDict | None) -> JsonDict:
    # Ensure `jsonDict` is not None.
    if jsonDict is None:
        raise TypeError(error.generateTypeError(jsonDict, JsonDict, "JSON file"))
    return jsonDict


def normalizeRequest(request: Request | Path | str) -> Request:
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
