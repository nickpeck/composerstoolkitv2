import unittest

from . import (testcore, testresources)

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromModule(testcore))
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromModule(testresources))
    return test_suite

if __name__ == '__main__':
    suite = suite()
    runner=unittest.TextTestRunner()
    outcome = runner.run(suite)
    print(outcome)
    was_successful = outcome.wasSuccessful()
    if was_successful:
        exit(0)
    exit(1)