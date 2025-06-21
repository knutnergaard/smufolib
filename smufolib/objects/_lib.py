from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from smufolib.objects.glyph import Glyph
    from smufolib.objects.font import Font


def getLibSubdict(obj: Font | Glyph | None, key: str) -> dict | None:
    """Return a mutable subdictionary from the given object's lib.

    If the subdict does not exist, it will be created and inserted
    automatically using an empty dictionary.

    :param obj: The lib's parent object.
    :param key: The top-level lib key for the desired subdict.

    """
    if obj is None:
        return None
    return obj.lib.naked().setdefault(key, {})


def updateLibSubdict(obj: Font | Glyph | None, libKey: str, value: Any) -> None:
    """Set or remove a top-level subdict in the object's lib.

    If `value` is falsy (e.g., ``None`` or ``{}``), the lib key will be removed.


    :param obj: The lib's parent object.
    :param libKey: The top-level lib key for the desired subdict.
    :param value: The new value for the subdict.

    """
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
    """Set or remove a single value inside a subdict in the object's lib.

    If `value` is falsy, the entry will be removed.
    If the subdict becomes empty as a result, the entire subdict key
    will be deleted from the lib.

    :param obj: The lib's parent object.
    :param libKey: The top-level lib key for the desired subdict.
    :param valueKey: The key for the value to set or remove.
    :param value: The new value for the subdict.

    """
    if obj is None:
        return
    lib = obj.lib.naked()
    subdict = lib.get(libKey, {})
    if not value:
        subdict.pop(valueKey, None)
        if libKey in lib and not lib[libKey]:
            del lib[libKey]
    else:
        lib.setdefault(libKey, {})[valueKey] = value
