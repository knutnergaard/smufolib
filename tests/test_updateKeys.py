import unittest
from unittest.mock import MagicMock, patch, call
from migration.updateKeys import rename_keys, process_font, expand_paths


class TestUpdateKeys(unittest.TestCase):
    def setUp(self):
        # Mock font lib with old keys
        self.mock_lib = {
            "_classes": ["class1", "class2"],
            "_designSize": 240,
            "_description": "Test font",
            "_engravingDefaults": {"key": "value"},
            "_name": "TestFont",
            "_names": ["Name1", "Name2"],
            "_sizeRange": (10, 20),
            "_spaces": 1.0,
        }

        # Expected lib after renaming keys
        self.expected_lib = {
            "com.smufolib.classes": ["class1", "class2"],
            "com.smufolib.designSize": 240,
            "com.smufolib.description": "Test font",
            "com.smufolib.engravingDefaults": {"key": "value"},
            "com.smufolib.name": "TestFont",
            "com.smufolib.names": ["Name1", "Name2"],
            "com.smufolib.sizeRange": (10, 20),
            "com.smufolib.spaces": 1.0,
        }

    def test_rename_keys(self):
        """Test that rename_keys correctly renames old keys to new keys."""
        rename_keys(self.mock_lib)
        self.assertEqual(self.mock_lib, self.expected_lib)

    @patch("migration.updateKeys.rename_keys")
    @patch("migration.updateKeys.Font")
    @patch("migration.updateKeys.tqdm")
    def test_process_font(self, mock_tqdm, mock_font, mock_rename_keys):
        """Test that process_font updates font and glyph lib keys."""
        # Mock font and glyphs
        mock_font_instance = MagicMock()
        mock_font_instance.lib = self.mock_lib
        mock_font_instance.__iter__.return_value = [
            MagicMock(lib=self.mock_lib) for _ in range(3)
        ]
        mock_font.return_value = mock_font_instance

        # Call process_font
        process_font("test.ufo")

        # Check that rename_keys was called for font lib and each glyph lib
        rename_calls = [call(self.mock_lib)] * 4  # 1 for font, 3 for glyphs
        self.assertEqual(mock_rename_keys.call_count, 4)

        # Check that font.save() was called
        mock_font_instance.save.assert_called_once()

    @patch("os.path.isdir")
    @patch("glob.glob")
    def test_expand_paths(self, mock_glob, mock_isdir):
        """Test that expand_paths correctly expands directories into UFO font files."""
        mock_isdir.side_effect = lambda path: path == "dir"
        mock_glob.return_value = ["dir/font1.ufo", "dir/font2.ufo"]

        paths = ["dir", "file.ufo"]
        expanded_paths = expand_paths(paths)

        self.assertEqual(expanded_paths, ["dir/font1.ufo", "dir/font2.ufo", "file.ufo"])
        mock_glob.assert_called_once_with("dir/*.ufo")


if __name__ == "__main__":
    unittest.main()
