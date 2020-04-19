"""
Tool Kit for writing tests
"""

__all__ = (
    "TestCase",
    "TestSuite",

    "assert_eq",
    "assert_ne",
    "assert_true",
    "assert_false",
    "assert_is",
    "fail",

    "run"
)

from . import runner
from . import report

class TestCase(object):
    """
    Decorator for a test case class
    """
    def __init__(self, name_or_func=None, suite=None):
        self.suite_name = suite
        if callable(name_or_func):
            self.test_name = name_or_func.__name__
            runner.Test_items.add_test(self.test_name, self.suite_name, name_or_func)
        else:
            self.test_name = name_or_func

    def __call__(self, test_class):
        """Only called if decorating a class

        Args:
            test_class (object) : The Class to be used as a test case
        """
        if self.test_name is None:
            self.test_name = test_class.__name__
        runner.Test_items.add_test(self.test_name, self.suite_name, test_class)


class TestSuite(object):
    """
    Decorator for a test suite class
    """
    def __init__(self, name_or_func=None):
        if callable(name_or_func):
            self.suite_name = name_or_func.__name__
            runner.Test_items.add_suite(self.suite_name, name_or_func)
        else:
            self.suite_name = name_or_func

    def __call__(self, suite_class):
        """Only called if decorating a class

        Args:
            suite_class (object) : The Class to be used as a test suite
        """
        if self.suite_name is None:
            self.suite_name = suite_class.__name__
        runner.Test_items.add_suite(self.suite_name, suite_class)


def assert_eq(arg1, arg2, msg=None):
    """Given that __eq__ can be overloaded, we must
    explicitly use the == operator

    Args:
        arg1 (object) : Argument 1
        arg2 (object) : Argument 2
        msg (string): Message to print when it fails

    Raises:
        report.TestException
    """
    good = bool(arg1 == arg2)
    if not good:
        raise report.TestException((arg1, arg2), msg)


def assert_ne(arg1, arg2, msg=None):
    """Given that __ne__ can be overloaded, we must
    explicitly use the != operator

    Args:
        arg1 (object) : Argument 1
        arg2 (object) : Argument 2
        msg (string): Message to print when it fails

    Raises:
        report.TestException
    """
    good = bool(arg1 != arg2)
    if not good:
        raise report.TestException((arg1, arg2), msg)


def assert_true(arg1, msg=None):
    """Check if arg1 is true

    Args:
        arg1 (object) : Argument 1
        msg (string): Message to print when it fails

    Raises:
        report.TestException
    """
    if not arg1:
        raise report.TestException((arg1,), msg)


def assert_false(arg1, msg=None):
    """Check if arg1 is false

    Args:
        arg1 (object) : Argument 1
        msg (string): Message to print when it fails

    Raises:
        report.TestException
    """
    if arg1:
        raise report.TestException((arg1,), msg)


def assert_is(arg1, arg2, msg=None):
    """Check if arg1 is arg2

    Args:
        arg1 (object) : Argument 1
        arg2 (object) : Argument 2
        msg (string): Message to print when it fails

    Raises:
        report.TestException
    """
    if arg1 is not arg2:
        raise report.TestException((arg1, arg2), msg)


def fail(msg=None):
    """Raises the exception

    Args:
        msg (string): Message to print when it fails

    Raises:
        report.TestException
    """
    raise report.TestException((), msg)


def run(test_name=None):
    """Run a test

    Args:
        test_name (string): Name of the test
    """
    runner.Test_items.check_consistancy()
    if test_name is None:
        names = runner.Test_items.get_all_test_names()
    else:
        names = [test_name]
    suite_runner = runner.SuiteRunner()
    for name in names:
        print("Running test case '%s'" % name)
        suite_class, test_class = runner.Test_items.get_test(name)
        suite_runner.switch_suites(suite_class)
        test_run = runner.TestRunner(name, test_class, suite_runner)
        test_run.run()
    suite_runner.switch_suites(None)

