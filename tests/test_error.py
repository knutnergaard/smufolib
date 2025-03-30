import unittest
from unittest.mock import patch
from pathlib import Path
from smufolib.error import (
    generateErrorMessage,
    generateTypeError,
    validateType,
    suggestValue,
    _listTypes,
)


def _expected_type_error_substrings(value, valid_types, object_name):
    """Generate expected substrings for a TypeError message."""
    type_names = _listTypes(valid_types)
    return type(value).__name__, type_names, object_name


class TestErrorGeneration(unittest.TestCase):
    def test_generateErrorMessage(self):
        message = generateErrorMessage(
            "typeError", objectName="index", validTypes="int", value="str"
        )
        expected_substrings = ("type", "index", "int", "str")

        for substring in expected_substrings:
            with self.subTest(substring=substring):
                self.assertIn(substring, message)

    def test_generateTypeError_with_single_type(self):
        value = 123
        valid_types = str
        object_name = "path"

        message = generateTypeError(value, (valid_types,), object_name)
        expected_substrings = _expected_type_error_substrings(
            value, valid_types, object_name
        )

        for substring in expected_substrings:
            with self.subTest(substring=substring):
                self.assertIn(substring, message)

    def test_generateTypeError_with_union_types(self):
        value = 123
        valid_types = str | Path
        object_name = "path"

        message = generateTypeError(value, valid_types, object_name)
        expected_substrings = _expected_type_error_substrings(
            value, valid_types, object_name
        )

        for substring in expected_substrings:
            with self.subTest(substring=substring):
                self.assertIn(substring, message)

    def test_generateTypeError_with_dependency(self):
        with patch("smufolib.error.generateErrorMessage") as mock_generate:
            value = 123
            valid_type = str
            object_name = "path"

            generateTypeError(
                value, valid_type, object_name, dependencyInfo="some_dependency"
            )
            str_value, str_type, object_name = _expected_type_error_substrings(
                value, valid_type, object_name
            )
            mock_generate.assert_called_with(
                "dependentTypeError",
                validTypes=str_type,
                objectName=object_name,
                dependencyInfo="some_dependency",
                value=str_value,
            )

    def test_generateTypeError_with_dependent_items(self):
        "Items in '{objectName}' must be {validTypes} when {dependencyInfo}, not {value}."
        with patch("smufolib.error.generateErrorMessage") as mock_generate:
            value = 123
            valid_type = str
            object_name = "path"

            generateTypeError(
                value,
                valid_type,
                object_name,
                dependencyInfo="some_dependency",
                items=True,
            )
            str_value, str_type, object_name = _expected_type_error_substrings(
                value, valid_type, object_name
            )
            mock_generate.assert_called_with(
                "dependentItemsTypeError",
                validTypes=str_type,
                objectName=object_name,
                dependencyInfo="some_dependency",
                value=str_value,
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
