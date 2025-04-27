import configparser
import os
import shutil
import unittest
from pathlib import Path
from unittest import mock

from tests.testUtils import SavedConfigMixin
from smufolib import config


class TestConfig(SavedConfigMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.config = """
[request]
encoding = utf-8
warn = yes

[settings]
number = 42
factor = 2.5
flag = true
values = (1, 2.0, three)
iterable = (string.)

[metadata.fallbacks]
source = rel/path/to/resource.json
        """
        self.configPath = self.saveConfigToTemp(filename="original.cfg")

    def test_load_from_explicit_path(self):
        loaded = config.load(self.configPath)
        self.assertEqual(loaded["request"]["encoding"], "utf-8")
        self.assertTrue(loaded["request"]["warn"])
        self.assertEqual(loaded["settings"]["number"], 42)
        self.assertEqual(loaded["settings"]["factor"], 2.5)
        self.assertTrue(loaded["settings"]["flag"])
        self.assertEqual(loaded["settings"]["values"], (1, 2.0, "three"))
        self.assertEqual(loaded["settings"]["iterable"], ("string.",))

    def test_relative_path_resolution(self):
        loaded = config.load(self.configPath)
        expectedPath = str(
            (self.configPath.parent / "rel/path/to/resource.json").resolve()
        )
        self.assertEqual(loaded["metadata.fallbacks"]["source"], expectedPath)

    @mock.patch("smufolib.config.Path.cwd")
    def test_load_from_cwd(self, mock_cwd):
        mock_cwd.return_value = self.tempPath
        fallbackPath = self.tempPath / "smufolib.cfg"
        shutil.copy(self.configPath, fallbackPath)
        loaded = config.load(None)
        self.assertIn("request", loaded)

    @mock.patch("smufolib.config.Path.home")
    def test_load_from_home(self, mock_home):
        mock_home.return_value = self.tempPath
        fallbackPath = self.tempPath / "smufolib.cfg"
        shutil.copy(self.configPath, fallbackPath)
        loaded = config.load(None)
        self.assertIn("settings", loaded)

    @mock.patch("smufolib.config.Path.cwd", return_value=Path("/nonexistent"))
    @mock.patch("smufolib.config.Path.home", return_value=Path("/nonexistent"))
    @mock.patch.dict(os.environ, {"SMUFOLIB_CFG": ""})
    @mock.patch(
        "smufolib.config.importlib.resources.files", return_value=Path("/nonexistent")
    )
    def test_all_fallbacks_fail(self, *mocks):
        with self.assertRaises(FileNotFoundError):
            config.load(None)

    @mock.patch.dict(os.environ, {}, clear=True)
    @mock.patch("smufolib.config.importlib.resources.files")
    def test_load_from_package_resource(self, mock_files):
        # Simulate importlib.resources.files("smufolib").joinpath("smufolib.cfg")
        mock_files.return_value.joinpath.return_value = self.configPath
        loaded = config.load(None)
        self.assertEqual(loaded["settings"]["number"], 42)

    def test_no_basepath_in_metadata_fallbacks(self):
        # pylint: disable=W0212
        parser = config._readConfigFile(self.configPath)

        if hasattr(parser, "basePath"):
            delattr(parser, "basePath")

        result = config._parse(parser, "metadata.fallbacks", "source")
        self.assertEqual(result, "rel/path/to/resource.json")  # result should be str

    def test_absolute_path_not_resolved(self):
        # pylint: disable=W0212
        absPath = str(Path(self.tempPath / "some/absolute/path.json").resolve())
        absPathConfig = f"""
    [metadata.fallbacks]
    source = {absPath}
        """
        configPath = self.saveConfigToTemp(config=absPathConfig, filename="abs.cfg")
        parser = config._readConfigFile(configPath)
        parser.basePath = Path("/should/not/be/used")
        result = config._parse(parser, "metadata.fallbacks", "source")
        self.assertEqual(result, absPath)
