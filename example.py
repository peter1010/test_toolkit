from test_toolkit import *

@TestCase("Test1")
def func(env):
    print("-- Test1:")
    assert False, "Wibble"

@TestCase("Test2")
def func(env):
    print("-- Test2:")

@TestCase
def Test3():
    print("-- Test3:")
    fail("Wobble")


@TestCase("Test4")
class mytest(object):

    def run(self):
        print("Test4::run")
        a = 10
        b = 11
        assertEqual(a, 
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
        assertEqual(env["CFG"], 13)

    def tearDown(self, env):
        print("Test5::tearDown")
        print(env["CFG"])

    def __del__(self):
        print("Test5::del")

@TestCase("Test6", "Suite1")
class myOtherTest:
    def run(self, env):
        raise RuntimeError("pooh")
#        fail("test")

@TestSuite
class Suite1:
    def setUp(self, env):
        env["BING"] = 3

    def tearDown(self, env):
        del env["BING"]


def main():
    print("running")
    run()

main()
