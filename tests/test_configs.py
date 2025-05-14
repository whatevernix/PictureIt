import unittest, os
from src.utils import configs


class TestConfigs(unittest.TestCase):
    def setUp(self):
        self.curDir = os.getcwd().replace("\\", "/") + "/tests"

    def test_open_yaml(self):
        res = configs.yaml_open(self.curDir + "/mediaTest.yaml")
        self.assertEqual(
            res,
            {"FileTypes": {"Accepted": ["jpg", "jpeg"]}},
        )


if __name__ == "__main__":
    unittest.main()
