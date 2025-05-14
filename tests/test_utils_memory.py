import unittest, os
from src.utils import memory
import psutil


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.curDir = os.getcwd().replace("\\", "/") + "/tests"

    def test_getWholeMemorySize(self):
        res = memory.getWholeMemorySize()
        res2 = psutil.virtual_memory().total
        self.assertEqual(res, res2)

    def test_getUsedMemorySize(self):
        res = memory.getUsedMemorySize()
        res2 = psutil.virtual_memory().total
        self.assertTrue(res < res2)

    def test_getFreeMemorySize(self):
        res = memory.getFreeMemorySize()
        res2 = psutil.virtual_memory().total
        self.assertTrue(res > 0)
        self.assertTrue(res < res2)

    def test_checkMemoryFit(self):
        with self.assertRaises(Exception) as context:

            memory.checkMemoryFit(filesize=150, memory_free=10)
            self.assertEqual("Memory Limit Reached." in context.exception)

        res = memory.checkMemoryFit(filesize=500, memory_free=10240)
        self.assertTrue(res)


if __name__ == "__main__":
    unittest.main()
