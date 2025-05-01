import unittest
from unittest.mock import patch, mock_open, MagicMock, PropertyMock
import urllib.error
import warnings
import json
from smufolib.request import Request, writeJson, CONFIG
from smufolib.utils.error import URLWarning


# pylint: disable=W0212, W0613


class TestRequest(unittest.TestCase):
    def setUp(self):
        self.path = "http://example.com"
        self.fallback = "fallback.txt"
        self.request = Request(path=self.path, fallback=self.fallback, warn=False)

    def test_repr(self):
        reprString = (
            f"<Request '{self.path}' ('{self.fallback}') at {id(self.request)}>"
        )
        self.assertEqual(repr(self.request), reprString)

    @patch.object(Request, "_getMetadata", return_value={"some": "data"})
    def test_classes(self, mock_getMetadata):
        result = Request.classes()
        mock_getMetadata.assert_called_once_with("classes", decode=True)
        self.assertEqual(result, {"some": "data"})

    @patch.object(Request, "_getMetadata", return_value={"some": "data"})
    def test_glyphnames(self, mock_getMetadata):
        result = Request.glyphnames()
        mock_getMetadata.assert_called_once_with("glyphnames", decode=True)
        self.assertEqual(result, {"some": "data"})

    @patch.object(Request, "_getMetadata", return_value={"some": "data"})
    def test_ranges(self, mock_getMetadata):
        result = Request.ranges()
        mock_getMetadata.assert_called_once_with("ranges", decode=True)
        self.assertEqual(result, {"some": "data"})

    @patch.object(Request, "_getMetadata", return_value={"some": "data"})
    def test_font(self, mock_getMetadata):
        result = Request.font()
        mock_getMetadata.assert_called_once_with("font", decode=True)
        self.assertEqual(result, {"some": "data"})

    @patch("urllib.request.urlopen")
    def test_readFromURL(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"data from URL"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        result = self.request._readFromURL()
        self.assertEqual(result, b"data from URL")

    def test_readFromUrl_with_path_none(self):
        self.request._path = None
        with self.assertRaises(TypeError):
            self.request._readFromURL()

    @patch("builtins.open", new_callable=mock_open, read_data="data from file")
    def test_readFromFallback(self, mock_file):
        result = self.request._readFromFallback()
        self.assertEqual(result, "data from file")

    def test_readFromFallback_without_fallback(self):
        self.request._fallback = None
        with self.assertRaises(TypeError):
            self.request._readFromFallback()

    @patch("builtins.open", new_callable=mock_open, read_data="data from file")
    def test_readFromPath(self, mock_file):
        self.request._path = "path.txt"
        result = self.request._readFromPath()
        self.assertEqual(result, "data from file")

    def test_readFromPath_without_path(self):
        self.request._path = None
        with self.assertRaises(TypeError):
            self.request._readFromPath()

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

    @patch("builtins.open", new_callable=mock_open, read_data="data from fallback")
    def test_raw_without_path(self, mock_file):
        self.request._path = None
        result = self.request.raw
        self.assertEqual(result, "data from fallback")

    def test_raw_without_path_and_fallback(self):
        self.request._path = None
        self.request._fallback = None
        self.assertIsNone(self.request.raw)

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_json(self, mock_file):
        self.request._path = "path.json"
        result = self.request.json()
        self.assertEqual(result, {"key": "value"})

    @patch.object(Request, "raw", new_callable=PropertyMock, return_value=None)
    def test_json_without_raw(self, mock_raw):
        self.assertIsNone(self.request.json())

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
        writtenContent = "".join(call.args[0] for call in handle.write.call_args_list)
        expectedContent = json.dumps(source, indent=4, sort_keys=False)
        self.assertEqual(writtenContent, expectedContent)

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
