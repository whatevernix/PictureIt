import unittest
import tests

loader = unittest.TestLoader()
start_dir = tests.__file__.replace("__init__.py", "")

suite = loader.discover(start_dir)

runner = unittest.TextTestRunner()
runner.run(suite)

# coverage run --source=src runTests.py
# coverage html
# open htmlcov/index.html
