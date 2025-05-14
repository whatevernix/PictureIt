import unittest
from src import media
from src.utils import mediaUtils
import os


class TestMediaUtils(unittest.TestCase):
    def setUp(self):
        self.curDir = os.getcwd().replace("\\", "/") + "/tests"

    def test_isMedia(self):
        with self.assertRaises(Exception) as context:

            mediaUtils.isMedia(file=self.curDir + "/__init__.py")
            self.assertEqual(
                "%s is Not Supported Media." % (self.curDir + "/__init__.py")
                in context.exception
            )
        res = mediaUtils.isMedia(file=self.curDir + "/images/test.copy.jpg")
        self.assertTrue(res)

    def test_getFrameNumber(self):
        with self.assertRaises(Exception) as context:

            mediaUtils.getFrameNumber(self.curDir + "/images/test.copy.jpg", False)
            self.assertEqual(
                "File Name %s Does not Follow name.frame.ext format" % self.curDir
                + "/images/test.copy.jpg"
                in context.exception
            )
        self.assertEqual(
            mediaUtils.getFrameNumber(self.curDir + "/images/test.1003.1006.jpg"),
            "1006",
        )
        self.assertEqual(
            mediaUtils.getFrameNumber(self.curDir + "/images/test.0999.jpg"),
            "0999",
        )

    def test_isMediaObject(self):
        self.assertTrue(mediaUtils.isMediaObject(media.Media()))

        x = "wrongInput"
        with self.assertRaises(Exception) as context:

            mediaUtils.isMediaObject(x)
            self.assertEqual("%s is not Media Type Class." % x in context.exception)

    def test_getSeqTemplatePath(self):
        res = mediaUtils.getSeqTemplatePath(self.curDir + "/images/test.1003.jpg")
        self.assertEqual(res, self.curDir + "/images/test.####.jpg")

    def test_generateBlankFrame(self):
        self.assertEqual(
            type(mediaUtils.generateBlankFrame(50, 50)).__name__, "ndarray"
        )

    def test_resizeImage(self):
        Media = media.Media()
        res = Media.readImage(file=self.curDir + "/images/test.copy.jpg")
        self.assertEqual([res.shape[0], res.shape[1]], [224, 417])
        res = mediaUtils.resizeImage(res, 150, 225)
        self.assertEqual([res.shape[0], res.shape[1]], [225, 150])

    def test_prepareForDisplay(self):
        Media = media.Media()
        res = Media.readImage(file=self.curDir + "/images/test.copy.jpg")
        _, format = mediaUtils.prepareForDisplay(res)
        self.assertEqual(format, "Format_RGB888")
        Media = media.Media()
        res = Media.readImage(file=self.curDir + "/images/exrtest.1005.exr")
        _, format = mediaUtils.prepareForDisplay(res)
        self.assertEqual(format, "Format_RGBA32FPx4")

    def test_figureHashSequenceName(self):
        file = mediaUtils.figureHashSequenceName(
            self.curDir + "/images/exrtest.####.exr"
        )
        self.assertEqual(file, self.curDir + "/images/exrtest.1001.exr")


if __name__ == "__main__":
    unittest.main()
