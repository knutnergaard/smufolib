# pylint: disable=C0103, C0114
from __future__ import annotations
from typing import Any, TypeVar

# Generic
T = TypeVar("T")

PairType = tuple[T, T]
QuadrupleType = tuple[T, T, T, T]
QuintupleType = tuple[T, T, T, T, T]
SextupleType = tuple[T, T, T, T, T, T]
CollectionType = list[T] | tuple[T, ...]
PairCollectionType = list[T] | PairType[T]
QuadrupleCollectionType = list[T] | QuadrupleType[T]
SextupleCollectionType = list[T] | SextupleType[T]

JsonDict = dict[str, Any]
EngravingDefaultsInput = int | float | CollectionType[str]
EngravingDefaultsReturn = int | float | tuple[str, ...]
