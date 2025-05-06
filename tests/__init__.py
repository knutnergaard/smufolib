import sys
import unittest
from tests.smufolib import (
    test_cli,
    test_config,
    test_request,
)
from tests.smufolib.objects import (
    test_engravingDefaults,
    test_font,
    test_glyph,
    test_range,
    test_smufl,
)
from tests.bin import (
    test_calculateEngravingDefaults,
    test_checkAnchors,
    test_cleanFont,
    test_generateMetadata,
    test_importAnchors,
    test_importID,
)
from tests.smufolib.utils import (
    test_converters,
    test_error,
    test_normalizers,
    test_pointUtils,
    test_rulers,
    test_scriptUtils,
    test_stdUtils,
)


def testEnvironment(objectGenerator, inApp=False, verbosity=1, testNormalizers=True):
    modules = [
        test_calculateEngravingDefaults,
        test_checkAnchors,
        test_cleanFont,
        test_cli,
        test_config,
        test_converters,
        test_engravingDefaults,
        test_error,
        test_generateMetadata,
        test_font,
        test_glyph,
        test_importAnchors,
        test_importID,
        test_pointUtils,
        test_range,
        test_request,
        test_rulers,
        test_smufl,
        test_scriptUtils,
        test_stdUtils,
    ]
    if testNormalizers:
        modules.append(test_normalizers)

    globalSuite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module in modules:
        suite = loader.loadTestsFromModule(module)
        _setObjectGenerator(suite, objectGenerator)
        globalSuite.addTest(suite)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    succes = runner.run(globalSuite).wasSuccessful()
    if not inApp:
        sys.exit(not succes)
    else:
        return succes  # pragma: no cover


def _setObjectGenerator(suite, objectGenerator):
    for i in suite:
        if isinstance(i, unittest.TestSuite):
            _setObjectGenerator(i, objectGenerator)
        else:
            i.objectGenerator = objectGenerator
