import sys
import os
import traceback

FILES_TO_IGNORE = (\
    __file__,
    os.path.join(os.path.dirname(__file__), "runner.py"),
    os.path.join(os.path.dirname(__file__), "toolkit.py"))


class TestException(Exception):
    """Exception raised by asserts
    """


def to_ignore(filename):
    """Files to ignore when analysising the exception traceback

    Args:
        filename (str): The filename

    Returns:
        bool: True if ignored
    """
    for fname in FILES_TO_IGNORE:
        if os.path.samefile(fname, filename):
            return True
    return False


def gather_test_exception(err, func_name):
    """Return the test exception as a string

    Args:
        err (Exception): The error
        func_name (str): The name of the assert that generated the test exception

    Returns:
        str: The string representation
    """
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


def gather_assert_exception(err):
    """Return the assert exception as a string

    Args:
        err (Exception): The error

    Returns:
        str: The string representation
    """
    msg = err.args[0]
    if msg is None:
        msg = ""
    failure_test = "assert False, %s" % (msg)
    return failure_test


def gather_other_exception(err):
    """Return the exception as a string

    Args:
        err (Exception): The error

    Returns:
        str: The string representation
    """
    return str(err)


class Report(object):
    """A test report

    Args:
        suite_name (str): The Suite this report belongs to
    """
    STARTED = 1
    FAILED = 2

    def __init__(self, suite_name):
        self.state = Report.STARTED
        self.msgs = []
        self.suite_name = suite_name
        self.test_name = None

    def copy(self, test_name):
        """Create a copy for test

        Args:
            test_name (str): Name of the test

        Returns:
            Report: A new report object for test_name
        """
        report = Report(self.suite_name)
        report.state = self.state
        report.msgs = self.msgs[:]
        report.test_name = test_name
        return report

    def is_failed(self):
        """Test if the report indicates a failure

        Returns:
            bool: True if failed
        """
        return self.state == Report.FAILED

    def log(self, msg):
        """log a message

        Args:
            msg (str): The message
        """
        self.msgs.append(msg)

    def failure(self, err):
        """Report the failure

        Args:
            err (Exception): The Exception
        """
        if self.state == Report.FAILED:
            return
        self.state = Report.FAILED
        _typ, _value, tbk = sys.exc_info()
        self.log("+-- FAILURE DETECTED! - back trace is ------")
        if tbk is None:
            self.no_traceback(err)
        else:
            tb_entries = traceback.extract_tb(tbk)
            indent = " "
            top_func = None
            for filename, line_num, func_name, text in tb_entries:
                top_func = func_name
                if to_ignore(filename):
                    continue

                self.log("|%sat line %i in  '%s'" % (indent, line_num, filename))
                self.log("|%s--> '%s'" % (indent, text))
                indent += "  "
            self.log("+-- Reason --")

            if isinstance(err, TestException):
                failure_test = gather_test_exception(err, top_func)
            elif isinstance(err, AssertionError):
                failure_test = gather_assert_exception(err)
            else:
                failure_test = gather_other_exception(err)
            self.log("| %s" % failure_test)
            self.log("+-------------------------------")


    def no_traceback(self, err):
        """Log no traceback

        Args:
            err (Exception): The exception that was thrown
        """
        self.log(str(err))
#       print(err)
#       traceback.print_stack()


