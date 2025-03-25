import unittest
from pathlib import Path
from smufolib import Request
from smufolib.error import (
    generateErrorMessage,
    generateTypeError,
    validateType,
    suggestValue,
    _listTypes,
)


class TestError(unittest.TestCase):
    def test_generateErrorMessage(self):
        message = generateErrorMessage("alphanumericValue", objectName="unicode")
        expected_message = "The value for 'unicode' must be alphanumeric."
        self.assertEqual(message, expected_message)

        message = generateErrorMessage(
            "typeError", objectName="index", validTypes="int", value="str"
        )
        expected_message = "Expected 'index' to be of type int, but got str."
        self.assertEqual(message, expected_message)

    def test_generateTypeError(self):
        message = generateTypeError(123, (str,), "path")
        expected_message = "Expected 'path' to be of type str, but got int."
        self.assertEqual(message, expected_message)

        message = generateTypeError(123, (str, Path), "path")
        expected_message = "Expected 'path' to be of type str or Path, but got int."
        self.assertEqual(message, expected_message)

        message = generateTypeError(123, (str, Path, Request), "path")
        expected_message = (
            "Expected 'path' to be of type str, Path or Request, but got int."
        )
        self.assertEqual(message, expected_message)

    def test_validateType(self):
        with self.assertRaises(TypeError) as context:
            validateType(123, str, "glyphName")
        self.assertEqual(
            str(context.exception),
            "Expected 'glyphName' to be of type str, but got int.",
        )

        validateType("uniE001", str, "glyphNames", items=True)

        with self.assertRaises(ValueError) as context:
            validateType(["uniE000", 1], str, "glyphNames", items=True)
        self.assertEqual(
            str(context.exception), "Items in 'glyphNames' must be str, not list."
        )

    def test_suggestValue(self):
        with self.assertRaises(ValueError) as context:
            suggestValue(
                "spiltStepUpSE",
                ["splitStemUpSE", "splitStemUpSW"],
                "anchorName",
                cutoff=0.5,
            )
        self.assertEqual(
            str(context.exception),
            "Invalid value for 'anchorName': spiltStepUpSE. Did you mean 'splitStemUpSE'?",
        )

        with self.assertRaises(ValueError) as context:
            suggestValue("invalidValue", ["validValue1", "validValue2"], "objectName")
        self.assertEqual(
            str(context.exception),
            "Invalid value for 'objectName': invalidValue. Did you mean 'validValue2'?",
        )

    def test_listTypes(self):
        self.assertEqual(_listTypes(str), "str")
        self.assertEqual(_listTypes((str, int)), "str or int")
        self.assertEqual(_listTypes((str, int, float)), "str, int or float")
