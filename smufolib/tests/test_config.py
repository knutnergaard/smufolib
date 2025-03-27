import unittest
from unittest.mock import patch, mock_open
from configparser import ConfigParser
import errno
from smufolib.config import load, _readConfigFile, _selectPath, _parse


class TestConfig(unittest.TestCase):
    # pylint: disable=W0613

    @patch("smufolib.config._readConfigFile")
    def test_load(self, mock_readConfigFile):
        mock_config = ConfigParser()
        mock_config.add_section("request")
        mock_config.set("request", "encoding", "utf-8")
        mock_config.set("request", "warn", "True")
        mock_readConfigFile.return_value = mock_config

        result = load()
        self.assertEqual(result["request"]["encoding"], "utf-8")
        self.assertEqual(result["request"]["warn"], True)

    @patch(
        "builtins.open", new_callable=mock_open, read_data="[section]\noption=value\n"
    )
    @patch("smufolib.config._selectPath", return_value="dummy_path")
    def test_readConfigFile(self, mock_selectPath, mock_open_file):
        result = _readConfigFile("dummy_path")
        self.assertIsInstance(result, ConfigParser)
        self.assertTrue(result.has_section("section"))
        self.assertEqual(result.get("section", "option"), "value")

    @patch("os.getenv", return_value=None)
    @patch(
        "pathlib.Path.exists", side_effect=[False, False, True]
    )  # Only three checks needed
    def test_selectPath(self, mock_exists, mock_getenv):
        result = _selectPath(None)
        self.assertTrue(result.endswith("smufolib.cfg"))

    @patch("os.getenv", return_value=None)
    @patch("pathlib.Path.exists", return_value=False)
    def test_selectPath_not_found(self, mock_exists, mock_getenv):
        with self.assertRaises(FileNotFoundError) as context:
            _selectPath(None)
        self.assertEqual(context.exception.errno, errno.ENOENT)

    def test_parse(self):
        config = ConfigParser()
        config.add_section("section")
        config.set("section", "int_option", "1")
        config.set("section", "float_option", "1.1")
        config.set("section", "bool_option", "True")
        config.set("section", "str_option", "string")
        config.set("section", "tuple_option", "(1, 2.2, string)")

        self.assertEqual(_parse(config, "section", "int_option"), 1)
        self.assertEqual(_parse(config, "section", "float_option"), 1.1)
        self.assertEqual(_parse(config, "section", "bool_option"), True)
        self.assertEqual(_parse(config, "section", "str_option"), "string")
        self.assertEqual(_parse(config, "section", "tuple_option"), (1, 2.2, "string"))
