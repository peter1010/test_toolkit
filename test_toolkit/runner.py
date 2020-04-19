import sys
import os
import traceback

from . import report

SETUP_METHODS = ("SetUp", "setUp", "setup")
RUN_METHODS = ("run", "Run")
TEARDOWN_METHODS = ("TearDown", "tearDown", "teardown")



def num_of_args(callable_obj):
    if hasattr(callable_obj, "__init__"):
        # Is the callable a class?
        if hasattr(callable_obj.__init__, "__code__"):
            return callable_obj.__init__.__code__.co_argcount - 1
    if hasattr(callable_obj, "__code__"):
        return callable_obj.__code__.co_argcount
    return 0
 

def get_impl_method(obj, poss_method_names):
    cnt = 0
    result = None
    for method_name in poss_method_names:
        if hasattr(obj, method_name):
            cnt += 1
            result = getattr(obj, method_name)
    assert cnt <= 1
    return result


class TestItem(tuple):

    def __new__(self, suite_name, test_class):
        return tuple.__new__(self, (suite_name, test_class))

    def get_suite_name(self):
        return self[0]

    def get_test_class(self):
        return self[1]


class TestItems(object):

    def __init__(self):
        self._test_items = {}
        self._test_suites = {}


    def add_test(self, name, suite, test_class):
        """Add a test object to list of test items

        Args:
            name (string): Name of the test
            suite (string): Name of the test suite the test belongs to
            test_class (callable): The test case (a class or function)
        """
        if name in self._test_items:
            raise RuntimeError("More than one test with same name, '%'" % name)
        self._test_items[name] = TestItem(suite, test_class)


    def add_suite(self, name, suite_class):
        """Add a suite object to list of suite items

        Args:
            name (string): Name of the Suite
            Suite_class (callable) : The suite (a class or function)
        """
        if name in self._test_suites:
            raise RuntimeError("More than one suite with same name, '%'" % name)
        self._test_suites[name] = suite_class


    def get_all_test_names(self):
        """Get all the test names

        Returns:
            list: List of names
        """
        return self._test_items.keys()


    def check_consistancy(self):
        avail_suite_names = set(self._test_suites.keys())
        used_suite_names = set()
        for _name, test_item in self._test_items.items():
            suite_name = test_item.get_suite_name()
            if suite_name is not None:
                used_suite_names.add(suite_name)
        assert avail_suite_names == used_suite_names


    def get_test(self, name):
        """Get a test item

        Args:
            name (string): Name of the test

        Returns:
            TestItem : The Item with the name
        """
        test_item = self._test_items[name]
        suite_name = test_item.get_suite_name()
        if suite_name is not None:
            suite_class = self._test_suites[suite_name]
        else:
            suite_class = None
        return suite_class, test_item.get_test_class()
        

Test_items = TestItems()



class TestRunner(object):

    def __init__(self, name, test_item, suite_runner):
        self.name = name
        self.test_class = test_item
        self.result_obj = suite_runner.init_result_obj.copy()
        self.env = suite_runner.get_env()


    def report_failure(self, err):
        if self.state == self.FAILED:
            return
        self.state = self.FAILED
        _typ, _value, tbk = sys.exc_info()
        print()
        print("+-- FAILURE DETECTED! - back trace is ------")
        if tbk is None:
            report_no_traceback(err)
        else:
            tb = traceback.extract_tb(tbk)
            indent = " "
            top_func = None
            for filename, line_num, func_name, text in tb:
                top_func = func_name
                if os.path.samefile(filename, __file__):
                    continue
                print("|%sat line %i in  '%s'" % (indent, line_num, filename))
                print("|%s--> '%s'" % (indent, text))
                indent += "  "
            print("+-- Reason --")
 
            if isinstance(err, TestException):
                failure_test = gather_test_exception(err, top_func)
            elif isinstance(err, AssertionError):
                failure_test = gather_assert_exception(err)
            else:
                failure_test = gather_other_exception(err)
            print("| %s" % failure_test)
            print("+-------------------------------")


    def set_up(self):
        args = num_of_args(self.test_class)
        try:
            if args > 0:
                test_obj = self.test_class(self.env)
            else:
                test_obj = self.test_class()
        except Exception as err:
            self.result_obj.failure(err)
            return None
        setup_func = get_impl_method(test_obj, SETUP_METHODS)
        if setup_func is not None:
            self.run_method(setup_func)
        return test_obj


    def tear_down(self, test_obj):
        teardown_method = get_impl_method(test_obj, TEARDOWN_METHODS)
        if teardown_method is not None:
            self.run_method(teardown_method)


    def run_method(self, func):
        try:
            if func.__code__.co_argcount > 1:
                func(self.env)
            else:
                func()
        except Exception as err:
            self.result_obj.failure(err)


    def run(self):
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

    def __init__(self):
        self._suite_class = None
        self._suite_obj = None
        self.init_result_obj = report.Report()
        
    def switch_suites(self, suite_class):
        """Switch to another suite

        Args:
            suite_class (callable) : Class or function

        Returns:
            bool: True on success
        """
        if self._suite_class is suite_class and not self.init_result_obj.is_failed():
            return
        self.tear_down()
        self._suite_class = suite_class
        self.set_up()

    def set_up(self):
        self.init_result_obj = report.Report()
        if self._suite_class is not None:
            try:
                self._suite_obj = self.suite_class()
            except Exception as err:
                self.init_result_obj.failure(err)
                return
            setup_func = get_impl_method(self._suite_obj, SETUP_METHODS)
            if setup_func is not None:
                try:
                    setup_func()
                except Exception as err:
                    self._init_result_obj.failure(err)

    def tear_down(self):
        if self._suite_obj is not None:
            teardown_func = get_impl_method(self._suite_obj, TEARDOWN_METHODS)
            if teardown_func is not None:
                teardown_func()
            del self._suite_obj
            self._suite_obj = None

    def get_env(self):
        """
        Get Suite environment variables
        """
        return {}


