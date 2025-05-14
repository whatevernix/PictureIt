import platform

_platform = platform.system()

from . import media
import time, threading, logging
from time import perf_counter as timer

if _platform == "Windows":
    from ctypes import windll

logger = logging.getLogger(__name__)


class Core(object):
    def __init__(self, cur_frame_signal=None, image_loaded_signal=None):
        self.Media_dic: dict = {}
        self.free_memory: float = 0
        self.project_name: str = None
        self.play_thread: object = None
        self.current_image: list = None
        self.current_frame: int = 0
        self.active_media: str = None
        self.is_playing: bool = False
        self.cur_frame_signal: object = cur_frame_signal
        self.image_loaded_signal: object = image_loaded_signal
        self.edited_seq: dict = {}
        self.start_frame: int = 0
        self.end_frame: int = 0
        self.fps_constant: float = 1
        self.cache_limit: float = 0.4

    def setCacheLimit(self):
        for M in self.Media_dic:
            self.Media_dic[M].memory_allowed_usage = self.cache_limit / 2

    def setFrame(self, value) -> None:
        self.current_frame = value
        if self.cur_frame_signal:
            self.cur_frame_signal.emit(self.current_frame)

    def addMedia(self, file, as_sequence=False, fps=0, wait=True) -> object:
        NewMedia = media.Media(self.image_loaded_signal)

        if as_sequence:
            NewMedia.loadSequence(file=file, fps=fps, wait_for_load=wait)

        else:
            NewMedia.loadImage(file=file)

        self.Media_dic[NewMedia.name] = NewMedia
        self.start_frame = int(NewMedia.full_frange[0])
        self.end_frame = int(NewMedia.full_frange[1])

        if wait:
            logger.info(f"{NewMedia.name} is loaded.")
        else:
            logger.info(f"{NewMedia.name} is being loaded...")

        return NewMedia

    def removeMedia(self, Media) -> None:
        if self.active_media == Media.name:
            self.active_media = None

        self.Media_dic.pop(Media.name, None)
        self.start_frame = 0
        self.end_frame = 0

    def getNextFrame(self) -> int:
        if self.current_frame >= self.end_frame:
            return self.start_frame

        return self.current_frame + 1

    def play(self) -> None:
        self.isMediaLoaded()

        self.is_playing = True
        self.play_thread = threading.Thread(target=self.playThread)
        self.play_thread.daemon = True
        self.play_thread.start()

    def editSequence(
        self, media_sequence, edits={}, threaded=True
    ) -> None:  # update test !
        t_list = []

        for media_key in media_sequence:
            if threaded:
                t = threading.Thread(
                    target=self._threadProcessImage,
                    args=(
                        media_sequence[media_key],
                        edits,
                        media_key,
                    ),
                )
                t.daemon = True
                t.start()
                t_list.append(t)
            else:
                self._threadProcessImage(media_sequence[media_key], edits, media_key)

        if t_list:
            for t in t_list:
                t.join()

    def _threadProcessImage(self, edited_image, edits, media_key) -> None:

        for key in edits:
            if key == "resize":
                edited_image = media.mediaUtils.resizeImage(
                    edited_image, edits[key][0], edits[key][1]
                )
        self.edited_seq[media_key] = edited_image

    def playThread(self) -> None:
        self.fps_constant = self.Media_dic[self.active_media].fps_constant

        if _platform == "Windows":
            timeBeginPeriod = windll.winmm.timeBeginPeriod
            timeBeginPeriod(1)

        prevTime = timer()

        while self.is_playing:

            curTime = timer()
            dif = curTime - prevTime
            if dif > self.fps_constant:

                for _ in range(int(dif / self.fps_constant)):

                    self.setFrame(self.getNextFrame())

                prevTime = timer()

            time.sleep(self.fps_constant / 10)

        return

    def isMediaLoaded(self) -> None:
        if self.active_media == None:
            raise Warning("Open Media First.")

    def changeFps(self, value) -> None:
        self.isMediaLoaded()
        self.Media_dic[self.active_media].fps = value
        self.fps_constant = self.Media_dic[self.active_media].getFpsConstant()
