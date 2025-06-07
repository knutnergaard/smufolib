from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from smufolib.objects.glyph import Glyph
    from smufolib.objects.font import Font


def getLibSubdict(obj: Font | Glyph | None, key: str) -> dict | None:
    if obj is None:
        return None
    return obj.lib.naked().setdefault(key, {})


def updateLibSubdict(obj: Font | Glyph | None, libKey: str, value: Any) -> None:
    # Common font metadata setter.
    if obj is None:
        return
    lib = obj.lib.naked()
    if not value:
        if libKey in lib:
            del lib[libKey]
    else:
        lib[libKey] = value


def updateLibSubdictValue(
    obj: Font | Glyph | None, libKey: str, valueKey: str, value: Any
) -> None:
    # Common font metadata setter.
    if obj is None:
        return
    lib = obj.lib.naked()
    subdict = lib.get(libKey, {})
    if value is None:
        subdict.pop(valueKey, None)
        if libKey in lib and not lib[libKey]:
            del lib[libKey]
    else:
        lib.setdefault(libKey, {})[valueKey] = value
