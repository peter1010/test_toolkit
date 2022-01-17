"""
The Test Runner
"""

from . import report

SETUP_METHODS = ("SetUp", "setUp", "setup")
RUN_METHODS = ("run", "Run")
TEARDOWN_METHODS = ("TearDown", "tearDown", "teardown")



def num_of_args(callable_obj):
    """Calculate number of arguments the callable object needs to take (ignoring self)

    Args:
        callable_obj (callable): The callable object to be checked

    Returns:
        int: The number of arguments
    """
    if hasattr(callable_obj, "__init__"):
        # Is the callable a class?
        if hasattr(callable_obj.__init__, "__code__"):
            return callable_obj.__init__.__code__.co_argcount - 1
    if hasattr(callable_obj, "__code__"):
        return callable_obj.__code__.co_argcount
    return 0


def get_impl_method(obj, poss_method_names):
    """Get bounded reference to method if it exists in the list of poss_method_names

    Args:
        obj (object): The object
        poss_method_names (list): List of method names

    Returns:
        callable or None: The bounded referenced method
    """
    cnt = 0
    result = None
    for method_name in poss_method_names:
        if hasattr(obj, method_name):
            cnt += 1
            result = getattr(obj, method_name)
    assert cnt <= 1
    return result


class TestItem(tuple):
    """A Named tuple of suite name and test case"""
    def __new__(cls, suite_name, test_class):
        return tuple.__new__(cls, (suite_name, test_class))

    def get_suite_name(self):
        """Return the test suite name

        Returns:
            str: The Test suite name
        """
        return self[0]

    def get_test_class(self):
        """Return the test class

        Returns:
            TestClass: The Test case
        """
        return self[1]


class TestItems(object):
    """A list of Test Cases & Test Suites
    """

    def __init__(self):
        self._test_items = {}


    def add_test(self, suite_class, test_class):
        """Add a test object to list of test items

        Args:
            name (string): Name of the test
            suite (string): Name of the test suite the test belongs to
            test_class (callable): The test case (a class or function)

        Raises:
            RuntimeError: When more than one test with same name
        """
        name = test_class.__name__
        if name in self._test_items:
            raise RuntimeError("More than one test with same name, '%s'" % name)
        self._test_items[name] = TestItem(suite_class, test_class)


    def get_all_test_names(self):
        """Get all the test names

        Returns:
            list: List of names
        """
        return self._test_items.keys()


    def get_test(self, name):
        """Get a test item

        Args:
            name (string): Name of the test

        Returns:
            str: The name of test suite
            SuiteClass: The Test Suite
            TestClass : The Test Case
        """
        test_item = self._test_items[name]
        suite_class = test_item.get_suite_name()
        if suite_class is not None:
            suite_name = suite_class.__name__
        else:
            suite_name = None
        return suite_name, suite_class, test_item.get_test_class()


Test_items = TestItems()



class TestRunner(object):
    """Test runner runs the corresponding Test Case

    Args:
        name (str): The name of the test
        test_class (class or func): The test case
        suite_runner (SuiteRunner): The Suite runner instance)
    """


    def __init__(self, name, test_class, suite_runner):
        self.test_class = test_class
        self.result_obj = suite_runner.init_result_obj.copy(name)
        self.env = suite_runner.get_env()


    def set_up(self):
        """Run the test setup
        """
        args = num_of_args(self.test_class)
        try:
            if args > 0:
                test_obj = self.test_class(self.env)
            else:
                test_obj = self.test_class()
        except Exception as err: # pylint: disable=broad-except
            self.result_obj.failure(err)
            return None
        setup_func = get_impl_method(test_obj, SETUP_METHODS)
        if setup_func is not None:
            self.run_method(setup_func)
        return test_obj


    def tear_down(self, test_obj):
        """Run the test tear down method (if one exists)

        Args:
            test_obj (object): The test object
        """
        teardown_method = get_impl_method(test_obj, TEARDOWN_METHODS)
        if teardown_method is not None:
            self.run_method(teardown_method)


    def run_method(self, func):
        """Run the method with right number of arguments and catch any exception

        Args:
            func (callable) : The function to call
        """
        try:
            if func.__code__.co_argcount > 1:
                func(self.env)
            else:
                func()
        except Exception as err: # pylint: disable=broad-except
            self.result_obj.failure(err)


    def run(self):
        """Run the Test Case
        """
        if self.result_obj.is_failed():
            return

        test_obj = self.set_up()
        if test_obj:

            if not self.result_obj.is_failed():
                run_func = get_impl_method(test_obj, RUN_METHODS)
                if run_func is not None:
                    self.run_method(run_func)

            self.tear_down(test_obj)
            del test_obj
        for msg in self.result_obj.msgs:
            print(msg)


class SuiteRunner(object):
    """Suite runner runs the corresponding TestSuite before running the TestSuite

    Args:
        env (dict): The initial env dictionary
    """

    def __init__(self, env):
        self._suite_class = None
        self._suite_obj = None
        self.init_result_obj = report.Report(None)
        if env:
            self.init_env = env
        else:
            self.init_env = {}
        self.env = self.init_env.copy()

    def switch_suites(self, suite_name, suite_class):
        """Switch to another suite

        Args:
            suite_name (str): Name of the Test Suite
            suite_class (callable) : Class or function
        """
        if self._suite_class is suite_class and not self.init_result_obj.is_failed():
            return
        self.tear_down()
        self._suite_class = suite_class
        self.set_up(suite_name)

    def set_up(self, suite_name):
        """Run the Suite setup

        Args:
            suite_name (str): Name of the suite
        """
        self.init_result_obj = report.Report(suite_name)
        self.env = self.init_env.copy()
        if self._suite_class is not None:
            args = num_of_args(self._suite_class)
            try:
                if args > 0:
                    self._suite_obj = self._suite_class(self.env)
                else:
                    self._suite_obj = self._suite_class()
            except Exception as err: # pylint: disable=broad-except
                self.init_result_obj.failure(err)
                return
            setup_func = get_impl_method(self._suite_obj, SETUP_METHODS)
            if setup_func is not None:
                self.run_method(setup_func)

    def run_method(self, func):
        """Run the method with right number of arguments and catch any exception

        Args:
            func (callable) : The function to call
        """
        try:
            if func.__code__.co_argcount > 1:
                func(self.env)
            else:
                func()
        except Exception as err: # pylint: disable=broad-except
            self.init_result_obj.failure(err)


    def tear_down(self):
        """Run the Suite tear down method (if one exists)
        """
        if self._suite_obj is not None:
            teardown_func = get_impl_method(self._suite_obj, TEARDOWN_METHODS)
            if teardown_func is not None:
                if teardown_func.__code__.co_argcount > 1:
                    teardown_func(self.env)
                else:
                    teardown_func()
            del self._suite_obj
            self._suite_obj = None

    def get_env(self):
        """Get Suite environment variables
        """
        return self.env

