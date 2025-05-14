import unittest
from src import media
import os, numpy


class TestMedia(unittest.TestCase):
    def setUp(self):
        self.curDir = os.getcwd().replace("\\", "/") + "/tests"

    def test_seqRangeFromFile(self):
        Media = media.Media()
        range = Media.seqRangeFromFile(self.curDir + "/images/test.1003.jpg")
        self.assertEqual(range, ["0999", "1005"])

    def test_loadSequence(self):
        Media = media.Media()
        res = Media.loadSequence(file=self.curDir + "/images/test.1001.jpg", fps=1)
        self.assertEqual(type(res[1003]).__name__, "ndarray")
        self.assertEqual(len(res), 7)
        Media = media.Media()
        res = Media.loadSequence(
            file=self.curDir + "/images/test.1001.jpg", fps=1, threaded=False
        )
        self.assertEqual(type(res[1003]).__name__, "ndarray")
        self.assertEqual(len(res), 7)
        Media = media.Media()
        res = Media.loadSequence(file=self.curDir + "/images/test.####.jpg", fps=1)
        self.assertEqual(type(res[1003]).__name__, "ndarray")
        self.assertEqual(len(res), 7)

    def test_loadImage(self):
        Media = media.Media()
        res = Media.loadImage(file=self.curDir + "/images/test.1001.jpg")
        self.assertEqual(type(res[0]).__name__, "ndarray")

        res = Media.loadImage(file=self.curDir + "/images/test.0999.jpg")
        self.assertEqual(type(res[0]).__name__, "ndarray")
        res = Media.loadImage(file=self.curDir + "/images/exrtest.1001.exr")
        self.assertEqual(type(res[0]).__name__, "ndarray")

    def test_readImage(self):
        Media = media.Media()
        res = Media.readImage(file=self.curDir + "/images/test.1004.jpg")
        self.assertEqual(type(res).__name__, "ndarray")
        b, g, r = res[0, 0]
        self.assertEqual([b, g, r], [93, 159, 64])

        res = Media.readImage(file=self.curDir + "/images/exrtest.1001.exr")
        self.assertEqual(type(res).__name__, "ndarray")
        b, g, r, a = res[res.shape[0] - 1, res.shape[1] - 1]
        b = numpy.round(b, 5)
        g = numpy.round(g, 5)
        r = numpy.round(r, 5)
        for ch1, ch2 in zip([b, g, r], [0.09084, 0.80695, 0.0]):
            self.assertAlmostEqual(ch1, ch2, delta=0.0001)

    def test_offload(self):
        Media = media.Media()
        res = Media.readImage(file=self.curDir + "/images/test.1001.jpg")
        self.assertEqual(type(res).__name__, "ndarray")
        Media.offload()
        self.assertEqual(Media.seq_images, {})

    def test_reload(self):
        Media = media.Media()
        res = Media.loadSequence(file=self.curDir + "/images/test.1001.jpg", fps=1)
        self.assertEqual(type(res[999]).__name__, "ndarray")
        Media.offload()
        self.assertEqual(Media.seq_images, {})
        Media.reload()
        self.assertTrue(Media.is_seq == True)
        self.assertEqual(type(Media.seq_images[1005]).__name__, "ndarray")
        Media.offload(1005)
        self.assertEqual(
            list(Media.seq_images.keys()), [999, 1000, 1001, 1002, 1003, 1004]
        )
        Media.reload(1005)
        self.assertEqual(type(Media.seq_images[1005]).__name__, "ndarray")
        Media = media.Media()
        res = Media.loadImage(file=self.curDir + "/images/test.1001.jpg")
        Media.offload()
        self.assertEqual(Media.seq_images, {})
        Media.reload()
        self.assertEqual(type(res[0]).__name__, "ndarray")

    def test_FpsConstant(self):
        Media = media.Media()
        Media.fps = 20
        self.assertTrue(Media.getFpsConstant() == 0.05)


if __name__ == "__main__":
    unittest.main()
