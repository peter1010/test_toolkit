"""
Example Test script
"""

from test_toolkit import *	#pylint: disable=wildcard-import


@TestCase
def test1(env):
	"""Test that 'assert False' works as expected"""
	print("-- Test1:")
	assert False, "Wibble"


@TestCase
def test2(env):
	"""Test that passes"""
	print("-- Test2:")


@TestCase
def test3():
	"""Test that 'fail' works as expected"""
	print("-- Test3:")
	fail("Wobble")


@TestCase
class Test4:
	"""Test as a class"""

	def __init__(self):
		self.aaa = 10
		self.bbb = 11

	def run(self):
		"""Run test that fails"""
		print("Test4::run")
		assert_eq(self.aaa,
				self.bbb,
				"failed")

@TestCase
class Test5():
	"""Test as a class"""

	def __init__(self):
		print("Test5::init")

	def set_up(self, env):
		print("Test5::setUp")
		env["CFG"] = 12

	def run(self, env):
		print("Test5::run")
		assert_eq(env["CFG"], 13)

	def tear_down(self, env):
		print("Test5::tearDown")
		print(env["CFG"])

	def __del__(self):
		print("Test5::del")

@TestSuite
class Suite1:
	def set_up(self, env):
		env["BING"] = 3

	def tear_down(self, env):
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
