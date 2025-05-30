import unittest
from unittest.mock import patch
from argparse import (
    ArgumentParser,
    HelpFormatter,
    RawTextHelpFormatter,
    ArgumentDefaultsHelpFormatter,
)
from smufolib.cli import REQUIRED, CONFIG, commonParser, createHelpFormatter
from tests.testUtils import SuppressOutputMixin


class TestCLI(SuppressOutputMixin, unittest.TestCase):
    def test_commonParser_basic(self):
        parser = commonParser("clear", addHelp=False)
        args = parser.parse_args(["--clear"])
        self.assertTrue(args.clear)

    def test_commonParser_as_parent(self):
        args = commonParser("color", "clear", addHelp=False)
        parser = ArgumentParser(parents=[args], description="showcase commonParser")
        parser.add_argument(
            "-O",
            "--include-optionals",
            action="store_true",
            help="include optional glyphs",
            dest="includeOptionals",
        )
        parsed_args = parser.parse_args(
            ["1", "2", "3", "4", "--clear", "--include-optionals"]
        )
        self.assertEqual(parsed_args.color, [1, 2, 3, 4])
        self.assertTrue(parsed_args.clear)
        self.assertTrue(parsed_args.includeOptionals)

    def test_commonParser_with_custom_helpers(self):
        customHelper = {"color": "custom help for color"}
        parser = commonParser("color", "clear", customHelpers=customHelper)
        args = parser.parse_args(["1", "2", "3", "4", "--clear"])
        self.assertEqual(args.color, [1, 2, 3, 4])
        self.assertTrue(args.clear)
        help_message = parser.format_help()
        self.assertIn("custom help for color", help_message)

    def test_commonParser_argument_conflict(self):
        with self.assertRaises(ValueError):
            commonParser("color", color=[1, 2, 3, 4])

    @patch.dict(CONFIG, {"cli": {"markRequired": False}})
    def test_commonParser_required_argument(self):
        parser = commonParser(color=REQUIRED, addHelp=False)
        result = [1, 2, 3, 4]
        args = parser.parse_args(["--color", "1", "2", "3", "4"])
        with self.assertRaises(SystemExit):
            self.suppressOutput()
            args = parser.parse_args(["--color"])
        self.assertEqual(repr(REQUIRED), "<Required>")
        self.assertEqual(args.color, result)

    def test_createHelpFormatter_single(self):
        formatter_class = createHelpFormatter("RawTextHelpFormatter")
        self.assertTrue(issubclass(formatter_class, HelpFormatter))
        self.assertTrue(issubclass(formatter_class, RawTextHelpFormatter))

    def test_createHelpFormatter_multiple(self):
        formatter_class = createHelpFormatter(
            ("RawTextHelpFormatter", "ArgumentDefaultsHelpFormatter")
        )
        self.assertTrue(issubclass(formatter_class, HelpFormatter))
        self.assertTrue(issubclass(formatter_class, RawTextHelpFormatter))
        self.assertTrue(issubclass(formatter_class, ArgumentDefaultsHelpFormatter))

    def test_createHelpFormatter_invalid_type(self):
        with self.assertRaises(TypeError) as context:
            createHelpFormatter(123)
        self.assertIn("Expected 'formatters' to be of type", str(context.exception))

    def test_createHelpFormatter_invalid_formatter(self):
        with self.assertRaises(ValueError) as context:
            createHelpFormatter("InvalidFormatter")
        self.assertIn("InvalidFormatter", str(context.exception))
