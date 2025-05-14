import unittest, os
import main


class TestConfigs(unittest.TestCase):
    def setUp(self):
        self.curDir = os.getcwd().replace("\\", "/") + "/tests"
        main.MainWindow()


if __name__ == "__main__":
    unittest.main()
