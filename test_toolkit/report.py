import sys
import os
import traceback

from . import report

FILES_TO_IGNORE = (\
    __file__, 
    os.path.join(os.path.dirname(__file__),"runner.py"),
    os.path.join(os.path.dirname(__file__), "toolkit.py")
)
 
class TestException(Exception):
    pass

 
def to_ignore(filename):
    for fname in FILES_TO_IGNORE:
        if os.path.samefile(fname, filename):
            return True
    return False

def gather_test_exception(err, func_name):
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
    msg = err.args[0]
    if msg is None:
        msg = ""
    failure_test = "assert False, %s" % (msg)
    return failure_test


def gather_other_exception(err):
    return str(err)


class Report(object):
    STARTED = 1
    FAILED = 2

    def __init__(self):
        self.state = Report.STARTED
        self.msgs = []

    def copy(self):
        report = Report()
        report.state = self.state
        report.msgs = self.msgs[:]
        return report

    def is_failed(self):
        return self.state == Report.FAILED

    def log(self, msg):
        self.msgs.append(msg)

    def failure(self, err):
        if self.state == Report.FAILED:
            return
        self.state = Report.FAILED
        _typ, _value, tbk = sys.exc_info()
        self.log("+-- FAILURE DETECTED! - back trace is ------")
        if tbk is None:
            self.no_traceback(err)
        else:
            tb = traceback.extract_tb(tbk)
            indent = " "
            top_func = None
            for filename, line_num, func_name, text in tb:
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
        self.log(str(err))
#       print(err)
#       traceback.print_stack()


