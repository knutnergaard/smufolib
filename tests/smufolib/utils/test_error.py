import unittest
from unittest.mock import patch
from pathlib import Path
from smufolib.utils.error import (
    generateErrorMessage,
    generateTypeError,
    validateType,
    suggestValue,
    _listTypes,
)


def _expected_type_error_substrings(value, validTypes, objectName):
    """Generate expected substrings for a TypeError message."""
    typeNames = _listTypes(validTypes)
    return type(value).__name__, typeNames, objectName


class TestErrorGeneration(unittest.TestCase):
    def test_generateErrorMessage(self):
        message = generateErrorMessage(
            "typeError", objectName="index", validTypes="int", value="str"
        )
        expectedSubstrings = ("type", "index", "int", "str")

        for substring in expectedSubstrings:
            with self.subTest(substring=substring):
                self.assertIn(substring, message)

    def test_generateTypeError_with_single_type(self):
        value = 123
        validTypes = str
        objectName = "path"

        message = generateTypeError(value, (validTypes,), objectName)
        expectedSubstrings = _expected_type_error_substrings(
            value, validTypes, objectName
        )

        for substring in expectedSubstrings:
            with self.subTest(substring=substring):
                self.assertIn(substring, message)

    def test_generateTypeError_with_union_types(self):
        value = 123
        validTypes = str | Path
        objectName = "path"

        message = generateTypeError(value, validTypes, objectName)
        expectedSubstrings = _expected_type_error_substrings(
            value, validTypes, objectName
        )

        for substring in expectedSubstrings:
            with self.subTest(substring=substring):
                self.assertIn(substring, message)

    def test_generateTypeError_with_dependency(self):
        with patch("smufolib.error.generateErrorMessage") as mock_generate:
            value = 123
            valid_type = str
            objectName = "path"

            generateTypeError(
                value, valid_type, objectName, dependencyInfo="some_dependency"
            )
            strValue, strType, objectName = _expected_type_error_substrings(
                value, valid_type, objectName
            )
            mock_generate.assert_called_with(
                "dependentTypeError",
                validTypes=strType,
                objectName=objectName,
                dependencyInfo="some_dependency",
                value=strValue,
            )

    def test_generateTypeError_with_dependent_items(self):
        "Items in '{objectName}' must be {validTypes} when {dependencyInfo}, not {value}."
        with patch("smufolib.error.generateErrorMessage") as mock_generate:
            value = 123
            valid_type = str
            objectName = "path"

            generateTypeError(
                value,
                valid_type,
                objectName,
                dependencyInfo="some_dependency",
                items=True,
            )
            strValue, strType, objectName = _expected_type_error_substrings(
                value, valid_type, objectName
            )
            mock_generate.assert_called_with(
                "dependentItemsTypeError",
                validTypes=strType,
                objectName=objectName,
                dependencyInfo="some_dependency",
                value=strValue,
            )

    def test_validateType(self):
        with self.assertRaises(TypeError) as ctx:
            validateType(123, str, "name")
        self.assertIn("Expected 'name' to be of type str", str(ctx.exception))

    def test_validateType_with_union_types(self):
        with self.assertRaises(TypeError) as ctx:
            validateType(123, str | float, "name")
        self.assertIn("Expected 'name' to be of type str or float", str(ctx.exception))

    def test_validateType_with_items(self):
        with self.assertRaises(ValueError) as ctx:
            validateType([123, "valid"], str, "items", items=True)
        self.assertIn("Items in 'items' must be str", str(ctx.exception))

    def test_suggestValue_suggests_correct_value(self):
        with self.assertRaises(ValueError) as ctx:
            suggestValue(
                "spiltStemUpSE",
                ["splitStemUpSE", "splitStemUpSW"],
                "anchorName",
                cutoff=0.5,
            )
        self.assertIn("Did you mean 'splitStemUpSE'?", str(ctx.exception))

    def test_suggestValue_no_suggestion(self):
        with self.assertRaises(ValueError) as ctx:
            suggestValue(
                "xyz", ["splitStemUpSE", "splitStemUpSW"], "anchorName", cutoff=0.9
            )
        self.assertNotIn("Did you mean", str(ctx.exception))
