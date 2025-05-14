import unittest, os, time
from src import core


def retry(times):
    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:

                try:
                    return func(*args, **kwargs)

                except:
                    attempt += 1

            return func(*args, **kwargs)

        return newfn

    return decorator


class TestCore(unittest.TestCase):
    def setUp(self):
        self.mediaType = None
        self.curDir = os.getcwd().replace("\\", "/") + "/tests"

    def test_addMedia_image(self):
        Core = core.Core()
        Core.addMedia(file=self.curDir + "/images/test.1001.jpg")
        self.assertEqual(len(Core.Media_dic), 1)
        self.assertTrue("test.1001.jpg" in Core.Media_dic)

    def test_addMedia_sequence(self):
        Core = core.Core()
        Core.addMedia(
            file=self.curDir + "/images/test.1001.jpg", as_sequence=True, fps=5
        )
        self.assertEqual(len(Core.Media_dic), 1)
        self.assertTrue("test.1001.jpg" in Core.Media_dic)

    def test_removeMedia(self):
        Core = core.Core()
        Res = Core.addMedia(file=self.curDir + "/images/test.1001.jpg")
        Core.removeMedia(Res)
        self.assertEqual(Core.Media_dic, {})
        Res = Core.addMedia(
            file=self.curDir + "/images/test.1001.jpg", as_sequence=True, fps=5
        )
        Core.removeMedia(Res)
        self.assertEqual(Core.Media_dic, {})

    def test_setFrame(self):
        Core = core.Core()
        Core.setFrame(0)
        self.assertEqual(Core.current_frame, 0)
        Core.addMedia(
            file=self.curDir + "/images/test.1001.jpg", as_sequence=True, fps=5
        )
        Core.setFrame(1001)
        self.assertEqual(Core.current_frame, 1001)

    def test_getNextFrame(self):
        Core = core.Core()
        Media = Core.addMedia(
            file=self.curDir + "/images/test.1001.jpg", as_sequence=True, fps=5
        )
        Core.active_media = Media.name
        Core.current_frame = 1001

        self.assertEqual(Core.getNextFrame(), 1002)

        Core.current_frame = 1005
        self.assertEqual(Core.getNextFrame(), 999)

    @retry(times=5)
    def test_play(self):
        Core = core.Core()
        Media = Core.addMedia(
            file=self.curDir + "/images/test.1001.jpg", as_sequence=True, fps=5
        )
        Core.active_media = Media.name
        Core.current_frame = 1001
        Core.play()
        time.sleep(0.5)
        Core.is_playing = False
        self.assertEqual(Core.current_frame, 1003)

    def test_editSequence(self):
        Core = core.Core()
        Media = Core.addMedia(
            file=self.curDir + "/images/test.1001.jpg", as_sequence=True, fps=5
        )
        Core.editSequence(Media.seq_images, {"resize": [512, 256]})
        self.assertTrue(Core.edited_seq[1001].shape[0] == 256)
        Core = core.Core()
        Media = Core.addMedia(
            file=self.curDir + "/images/test.1001.jpg",
            as_sequence=True,
            fps=5,
        )
        Core.editSequence(Media.seq_images, {"resize": [512, 256]}, threaded=False)
        self.assertTrue(Core.edited_seq[1001].shape[0] == 256)

    def test_changeFps(self):
        Core = core.Core()
        Media = Core.addMedia(
            file=self.curDir + "/images/test.1001.jpg", as_sequence=True, fps=7
        )
        Core.active_media = Media.name
        Core.current_frame = 1001
        Core.changeFps(2.1)
        Core.play()
        time.sleep(0.75)
        Core.is_playing = False
        self.assertEqual(Core.current_frame, 1002)

    def test_isMediaLoaded(self):
        Core = core.Core()
        with self.assertRaises(Exception) as context:

            Core.isMediaLoaded()
            self.assertEqual("Open Media First." in context.exception)


if __name__ == "__main__":
    unittest.main()
