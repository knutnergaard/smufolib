import unittest
from smufolib.config import load

# pylint: disable=C0115, C0116, C0103


class Config(unittest.TestCase):
    @classmethod
    def SetUpClass(cls):
        # Create config test file
        pass

    @classmethod
    def TearDownClass(cls):
        # Delete config test file
        pass

    def test_load(self):
        # Should test:
            # - value parsing
            # - path selection
            # - file integrity (exsistence, type and contents)
        pass


if __name__ == '__main__':
    unittest.main()
