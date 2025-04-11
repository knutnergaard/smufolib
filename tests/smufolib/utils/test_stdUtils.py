import io
import sys
import unittest
from smufolib.utils.stdUtils import (
    flatten,
    addTuples,
    getSummary,
    isFloat,
    validateClassAttr,
    doNothing,
    verbosePrint,
)


class StdUtils(unittest.TestCase):
    def test_flatten(self):
        self.assertEqual(
            list(flatten([1, [2, [3, [4, 5]]]], depth=2)), [1, 2, 3, [4, 5]]
        )
        self.assertEqual(
            list(flatten([1, [2, [3, [4, [5]]]]], depth=None)), [1, 2, 3, 4, 5]
        )
        self.assertEqual(list(flatten([])), [])
        self.assertEqual(list(flatten([1, 2, 3])), [1, 2, 3])

    def test_addTuples(self):
        self.assertEqual(addTuples((2, 4), (2, 4)), (4, 8))
        self.assertEqual(addTuples((1.5, 2.5), (2.5, 3.5)), (4.0, 6.0))
        self.assertEqual(addTuples((1,)), (1,))

    def test_getSummary(self):
        def example_function():
            """Example summary line.

            Detailed explanation follows.
            """

        self.assertEqual(getSummary(example_function.__doc__), "Example summary line.")
        self.assertIsNone(getSummary(None))
        self.assertEqual(getSummary(""), "")

    def test_isFloat(self):
        self.assertTrue(isFloat("3.14"))
        self.assertTrue(isFloat("0.0"))
        self.assertFalse(isFloat("314"))
        self.assertFalse(isFloat("abc"))
        self.assertFalse(isFloat("a.b"))
        self.assertFalse(isFloat(""))

    def test_validateClassAttr(self):
        class MyClass:
            def __init__(self):
                self.attr1 = 1
                self.attr2 = 2

        obj = MyClass()
        self.assertTrue(validateClassAttr(obj, ["attr1", "attr2"]))
        self.assertFalse(validateClassAttr(obj, "attr3"))
        self.assertTrue(validateClassAttr(obj, None))

    def test_doNothing(self):
        self.assertIsNone(doNothing(1, 2, 3))
        self.assertIsNone(doNothing(a=1, b=2))

    def test_verbosePrint(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput

        verbosePrint("Hello, world!", True)
        self.assertEqual(capturedOutput.getvalue().strip(), "Hello, world!")

        capturedOutput.truncate(0)
        capturedOutput.seek(0)

        verbosePrint("Hello, world!", False)
        self.assertEqual(capturedOutput.getvalue(), "")

        sys.stdout = sys.__stdout__  # Reset stdout
