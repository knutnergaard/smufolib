import unittest
from unittest.mock import patch, mock_open, MagicMock
import urllib.error
import warnings
import json
from smufolib.request import Request, writeJson, CONFIG
from smufolib.error import URLWarning


# pylint: disable=W0212, W0613


class TestRequest(unittest.TestCase):
    def setUp(self):
        self.path = "http://example.com"
        self.fallback = "fallback.txt"
        self.request = Request(path=self.path, fallback=self.fallback, warn=False)

    @patch("urllib.request.urlopen")
    def test_readFromURL(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"data from URL"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.request._readFromURL()
        self.assertEqual(result, b"data from URL")

    @patch("builtins.open", new_callable=mock_open, read_data="data from file")
    def test_readFromFallback(self, mock_file):
        result = self.request._readFromFallback()
        self.assertEqual(result, "data from file")

    @patch("builtins.open", new_callable=mock_open, read_data="data from file")
    def test_readFromPath(self, mock_file):
        self.request._path = "path.txt"
        result = self.request._readFromPath()
        self.assertEqual(result, "data from file")

    @patch("urllib.request.urlopen", side_effect=urllib.error.URLError("URL error"))
    @patch("builtins.open", new_callable=mock_open, read_data="data from fallback")
    def test_handleURLError_with_fallback(self, mock_file, mock_urlopen):
        result = self.request._readFromURL()
        self.assertEqual(result, "data from fallback")

    @patch("urllib.request.urlopen", side_effect=urllib.error.URLError("URL error"))
    def test_handleURLError_without_fallback(self, mock_urlopen):
        self.request._fallback = None
        with self.assertRaises(urllib.error.URLError):
            self.request._readFromURL()

    @patch("urllib.request.urlopen", side_effect=urllib.error.URLError("URL error"))
    @patch("builtins.open", new_callable=mock_open, read_data="data from fallback")
    def test_handleURLError_with_warning(self, mock_file, mock_urlopen):
        self.request._warn = True
        with warnings.catch_warnings(record=True) as w:
            result = self.request._readFromURL()
            self.assertEqual(result, "data from fallback")
            self.assertTrue(any(item.category == URLWarning for item in w))

    @patch("builtins.open", new_callable=mock_open, read_data="data from file")
    def test_raw(self, mock_file):
        self.request._path = "path.txt"
        result = self.request.raw
        self.assertEqual(result, "data from file")

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_json(self, mock_file):
        self.request._path = "path.json"
        result = self.request.json()
        self.assertEqual(result, {"key": "value"})

    def test_path(self):
        self.assertEqual(self.request.path, self.path)

    def test_fallback(self):
        self.assertEqual(self.request.fallback, self.fallback)

    def test_mode(self):
        self.assertEqual(self.request.mode, "r")

    def test_encoding(self):
        self.assertEqual(self.request.encoding, CONFIG["request"]["encoding"])


class TestWriteJson(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open)
    def test_writeJson(self, mock_file):
        filepath = "test.json"
        source = {"key": "value"}
        writeJson(filepath, source)
        mock_file.assert_called_once_with(
            filepath, "w", encoding=CONFIG["request"]["encoding"]
        )
        handle = mock_file()
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)
        expected_content = json.dumps(source, indent=4, sort_keys=False)
        self.assertEqual(written_content, expected_content)

    def test_writeJson_invalid_type(self):
        with self.assertRaises(TypeError):
            writeJson(123, {"key": "value"})

    def test_writeJson_invalid_extension(self):
        with self.assertRaises(ValueError):
            writeJson("test.txt", {"key": "value"})

    @patch("builtins.open", new_callable=mock_open)
    def test_writeJson_serialization_error(self, mock_file):
        source = {"key": set()}
        with self.assertRaises(ValueError):
            writeJson("test.json", source)
