import sys
import unittest
from smufolib.tests import test_cli
from smufolib.tests import test_config
from smufolib.tests import test_converters
from smufolib.tests import test_engravingDefaults
from smufolib.tests import test_error
from smufolib.tests import test_normalizers
from smufolib.tests import test_pointUtils
from smufolib.tests import test_range
from smufolib.tests import test_request
from smufolib.tests import test_smufl
from smufolib.tests import test_stdUtils


def testEnvironment(objectGenerator, inApp=False, verbosity=1, testNormalizers=True):
    modules = [
        test_cli,
        test_config,
        test_converters,
        test_engravingDefaults,
        test_error,
        test_pointUtils,
        test_range,
        test_request,
        test_smufl,
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
