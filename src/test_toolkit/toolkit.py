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

class TestCase:
	"""
    Decorator for a test case class
    """
	def __init__(self, suite_or_func):
		"""
        This is called when decorator is used. The argument depends on
        if @TestCase or @TestCase(suite) is used. In the first case
        the argument is the function to wrap. In the second case the
        argument is the suite and then __call_ is called
        """
		assert callable(suite_or_func)

		if hasattr(suite_or_func, "__name__"):
			runner.Test_items.add_test(None, suite_or_func)
		else:
			self.suite = suite_or_func.wrapped_suite
			del suite_or_func

	def __call__(self, test_func):
		"""Only called if decorating a class

        Args:
            test_class (object) : The Class to be used as a test case
        """
		runner.Test_items.add_test(self.suite, test_func)


class TestSuite:
	"""
    Decorator for a test suite class
    """
	def __init__(self, suite):
		assert callable(suite)
		self.wrapped_suite = suite

	def __call__(self):
		assert False

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


def run(test_name=None, env=None):
	"""Run a test

    Args:
        test_name (string): Name of the test
        env (dict): Dictionary of environment variables
    """
	if test_name is None:
		names = runner.Test_items.get_all_test_names()
	else:
		names = [test_name]
	suite_runner = runner.SuiteRunner(env)
	for name in names:
		print("Running test case '%s'" % name)
		suite_name, suite_class, test_class = runner.Test_items.get_test(name)
		suite_runner.switch_suites(suite_name, suite_class)
		test_run = runner.TestRunner(name, test_class, suite_runner)
		test_run.run()
	suite_runner.switch_suites(None, None)

