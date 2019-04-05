import sys
import os
import traceback

__all__ = (
    "TestCase",
    "TestSuite",

    "assertEqual",
    "assertNotEqual",
    "assertTrue",
    "assertFalse",
    "assertIs",
    "fail",

    "run"
)


_test_classes = {}
_test_suites = {}


def add_test(name, suite, test_class):
    _test_classes[name] = (suite, test_class)
    

def add_suite(name, suite_class):
    _test_suites[name] = suite_class


class TestCase(object):

    def __init__(self, name=None, suite=None):
        self.suite_name = suite
        if callable(name):
            self.test_name = name.__name__
            add_test(self.test_name, self.suite_name, name)
        else:
            self.test_name = name

    def __call__(self, test_class):
        if self.test_name is None:
            self.test_name = test_class.__name__
        add_test(self.test_name, self.suite_name, test_class)


class TestSuite(object):

    def __init__(self, name=None):
        if callable(name):
            self.suite_name = name.__name__
            add_suite(self.suite_name, name)
        else:
            self.suite_name = suite

    def __call__(self, suite_class):
        if self.suite_name is None:
            self.suite_name = suite_class.__name__
        add_suite(self.suite_name, suite_class)


class TestException(Exception):
    pass


def assertEqual(a, b, msg=None):
    if not(a == b):
        raise TestException((a, b), msg)


def assertNotEqual(a, b, msg=None):
    if not(a != b):
        raise TestException((a, b), msg)


def assertTrue(a, msg=None):
    if not (a):
        raise TestException((a,), msg)
    

def assertFalse(a, msg=None):
    if a:
        raise TestException((a,), msg)


def assertIs(a, b, msg=None):
    if a is not b:
        raise TestException((a, b), msg)


def fail(msg=None):
    raise TestException((), msg)


def reportNoTraceback(err):
    print(err)
#    print(err)
#    traceback.print_stack()



def gatherTestException(err, func_name):
    msg = err.args[1]
    args = err.args[0]
    if msg is None: 
        msg = ""
    if len(args) >= 2:
        failure_test = "%s(%s, %s), %s" % (func_name, str(args[0]), str(args[1]), msg)
    elif len(args) >= 1:
        failure_test = "%s(%s), %s" % (func_name, str(args[0]), msg)
    else:
        failure_test = "%s(), %s" % (func_name, msg)
    return failure_test


def gatherAssertException(err, func_name):
    msg = err.args[0]
    if msg is None: 
        msg = ""
    failure_test = "assert False, %s" % (msg)
    return failure_test


def gatherOtherException(err):
    return str(err)


class TestRunner(object):
    STARTED = 1
    FAILED = 2

    def __init__(self, name, test_class, env):
        self.name = name
        self.test_class = test_class
        self.state = self.STARTED
        self.env = env


    def reportFailure(self, err):
        if self.state == self.FAILED:
            return
        self.state = self.FAILED
        typ, value, tb = sys.exc_info()
        print()
        print("+-- FAILURE DETECTED! - back trace is ------")
        if tb is None:
            reportNoTraceback(err)
        else:
            tb = traceback.extract_tb(tb)
            indent = " "
            for filename, line_num, func_name, text in tb:
                if os.path.samefile(filename, __file__):
                    continue
                print("|%sat line %i in  '%s'" % (indent, line_num, filename)) 
                print("|%s--> '%s'" % (indent, text))
                indent += "  "
            print("+-- Reason --")
 
            if isinstance(err, TestException):
                failure_test = gatherTestException(err, func_name)
            elif isinstance(err, AssertionError):
                failure_test = gatherAssertException(err, func_name)
            else:
                failure_test = gatherOtherException(err)
            print("| %s" % failure_test)
            print("+-------------------------------")


    def createObj(self):
        args = 0
        if hasattr(self.test_class, ".__init__"):
            if hasattr(self.test_class.__init__, "__code__"):
                args = self.test_class.__init__.__code__.co_argcount - 1
        elif hasattr(self.test_class, "__code__"):
            args = self.test_class.__code__.co_argcount
        try:
            if args > 0:
                test_obj = self.test_class(self.env)
            else:
                test_obj = self.test_class()
        except Exception as err:
            self.reportFailure(err)
            test_obj = None
        return test_obj


    def runMethod(self, test_obj, name):
        if hasattr(test_obj, name):
            func = getattr(test_obj, name)
        else:
            func = None
        if func:
            try:
                if func.__code__.co_argcount > 1:
                    func(self.env)
                else:
                    func()
            except Exception as err:
                self.reportFailure(err)


    def run(self):
        test_obj = self.createObj()
        if test_obj:
            for methodName in ("SetUp", "setUp", "setup", "run", "Run"):
                self.runMethod(test_obj, methodName)
                if self.state == self.FAILED:
                    break
            for methodName in ("TearDown", "tearDown", "teardown"):
                self.runMethod(test_obj, methodName)
            try:
                del test_obj
            except Exception as err:
                self.reportFailure(err)

class SuiteRunner(object):

    def switchSuites(self, suite_class):
        pass

    def get_env(self):
        return {}


def run(name = None):
    if name is None:
        names = _test_classes.keys()
    else:
        names = [name]
    suite_runner = SuiteRunner()
    for name in names:
        print("Running test case '%s'" % name)
        suite, test_class = _test_classes[name]
        if suite != None:
            suite_class = _test_suites[suite]
        else:
            suite_class = None
        suite_runner.switchSuites(suite_class)
        runner = TestRunner(name, test_class, suite_runner.get_env())
        runner.run()
    suite_runner.switchSuites(None)

