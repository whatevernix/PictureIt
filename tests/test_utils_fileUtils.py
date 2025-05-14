import unittest
from src.utils import fileUtils
import os


class TestFileUtils(unittest.TestCase):
    def setUp(self):
        self.curDir = os.getcwd().replace("\\", "/") + "/tests"

    def test_isFile_raise(self):
        with self.assertRaises(Exception) as context:

            fileUtils.isFile(file=self.curDir + "/images/")
            self.assertEqual(
                "File is Requested, While %s Was Given." % (self.curDir + "/images/")
                in context.exception
            )

    def test_formatFilepath(self):
        path = self.curDir + "/images/test.jpg"
        path.replace("\\", "/")
        self.assertEqual(
            path, fileUtils.formatFilepath(self.curDir + r"\images\test.jpg")
        )

    def test_getFilename(self):
        self.assertEqual(
            "test.copy.jpg",
            fileUtils.getFilename(self.curDir + "/images/test.copy.jpg"),
        )
        with self.assertRaises(Exception) as context:

            fileUtils.isFile(file=self.curDir + "/images/test.jpg")
            self.assertEqual(
                "Can't find %s File." % (self.curDir + "/images/test.jpg")
                in context.exception
            )

    def test_splitStringByIndex(self):
        res = fileUtils.splitStringByIndex("test.0999.jpg")
        self.assertEqual(res, "0999")

        res = fileUtils.splitStringByIndex("test.1003.jpg", 0)
        self.assertEqual(res, "test")

    def test_combineFromArray(self):
        res = fileUtils.strFromArray(["a", "b", "c", "d", "e"], 1, 3)
        self.assertEqual(res, "b.c")

    def test_filterFileDirByExt(self):
        res = fileUtils.filterFileDirByExt(self.curDir + "/images/test.1003.jpg")
        expectedResult = [
            "somethingElse.jpg",
            "test.0999.jpg",
            "test.1000.jpg",
            "test.1001.jpg",
            "test.1002.jpg",
            "test.1003.jpg",
            "test.1003.1006.jpg",
            "test.1004.jpg",
            "test.1005.jpg",
            "test.copy.jpg",
        ]
        self.assertCountEqual(res, expectedResult)
        for r in res:
            self.assertTrue(r in expectedResult)

    def test_getFileSize(self):
        res = fileUtils.getFileSize(self.curDir + "/images/test.1003.jpg")
        self.assertEqual(res, 631)

    def getVariableSize(self):
        x = 10
        res = fileUtils.getVariableSize(x)
        self.asserEqual(x, 2)


if __name__ == "__main__":
    unittest.main()
