import unittest
from smufolib.error import (
    VALUE_ERROR,
    VALUE_SUGGESTION,
    MISSING_JSON_EXTENSION,
    TYPE_ERROR,
    URL_ERROR,
    MISSING_URL,
    MISSING_PATH,
    MISSING_PATH_AND_FALLBACK,
    SERIALIZATION_ERROR,
    URLWarning,
    generateErrorMessage,
    validateType,
    suggestValue
)

# pylint: disable=C0115, C0116, C0103


class Error(unittest.TestCase):

    def test_generateErrorMessage(self):
        parameter = 'testParameter'
        value = 'testValue'
        self.assertEqual(generateErrorMessage(
            VALUE_ERROR, parameter=parameter, value=value),
            f"Invalid value for parameter '{parameter}': '{value}'."
        )

    def test_validateType(self):
        pass

    def suggestValue(self):
        pass


if __name__ == '__main__':
    unittest.main()
