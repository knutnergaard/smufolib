# pylint: disable=C0103, C0114
from __future__ import annotations
from typing import Any, Literal, TypeVar

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

ErrorKey = Literal[
    "alphanumericValue",
    "alphanumericValueItems",
    "argumentConflict",
    "attributeError",
    "contextualAttributeError",
    "contextualItemsTypeError",
    "contextualSetAttributeError",
    "contextualTypeError",
    "deprecated",
    "deprecatedReplacement",
    "duplicateAttributeValue",
    "duplicateFlags",
    "duplicateItems",
    "emptyValue",
    "emptyValueItems",
    "fileNotFound",
    "invalidFormat",
    "invalidInitialCharacter",
    "invalidInitialItemsCharacter",
    "itemsTypeError",
    "itemsValueError",
    "missingDependency",
    "missingExtension",
    "missingGlyph",
    "missingValue",
    "nonIncreasingRange",
    "notImplementedError",
    "numericValue",
    "overlappingRange",
    "permissionError",
    "recommendScript",
    "serializationError",
    "singleItem",
    "suggestion",
    "typeError",
    "unicodeOutOfRange",
    "urlError",
    "valueError",
    "valueTooHigh",
    "valueTooLow",
]
