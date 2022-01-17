from test_toolkit import *


@TestCase
def Test1(env):
    """Test that 'assert False' works as expected"""
    print("-- Test1:")
    assert False, "Wibble"


@TestCase
def Test2(env):
    print("-- Test2:")


@TestCase
def Test3():
    """Test that 'fail' works as expected"""
    print("-- Test3:")
    fail("Wobble")


@TestCase
class Test4(object):

    def run(self):
        print("Test4::run")
        a = 10
        b = 11
        assert_eq(a, 
                b, 
                "failed")

@TestCase
class Test5():

    def __init__(self):
        print("Test5::init")

    def setUp(self, env):
        print("Test5::setUp")
        env["CFG"] = 12

    def run(self, env):
        print("Test5::run")
        assert_eq(env["CFG"], 13)

    def tearDown(self, env):
        print("Test5::tearDown")
        print(env["CFG"])

    def __del__(self):
        print("Test5::del")

@TestSuite
class Suite1:
    def setUp(self, env):
        env["BING"] = 3

    def tearDown(self, env):
        del env["BING"]


@TestCase(Suite1)
class Test6:
    def run(self, env):
        raise RuntimeError("pooh")
#        fail("test")


def main():
    print("running")
    run()

main()
