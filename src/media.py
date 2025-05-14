import os
from multiprocessing.pool import ThreadPool

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
import cv2, time
from functools import lru_cache
from src.utils import fileUtils, mediaUtils, memory


class Media:
    __slots__ = (
        "seq_images",
        "fps",
        "full_frange",
        "name",
        "fps_constant",
        "file",
        "is_seq",
        "memory_allowed_usage",
        "image_loaded_signal",
    )

    def __init__(self, image_loaded_signal=None):
        self.seq_images: dict = {}
        self.fps: float = 1
        self.full_frange: list[int, int] = [0, 0]
        self.name: str = None
        self.fps_constant: float = 0.0
        self.file: str = None
        self.is_seq: bool = False
        self.memory_allowed_usage: float = 0.2
        self.image_loaded_signal: object = image_loaded_signal

    def _fileChecks(self, file) -> None:
        fileUtils.isFile(file)
        mediaUtils.isMedia(file)

    def seqRangeFromFile(self, file) -> list:
        fnum: str = mediaUtils.getFrameNumber(file, silent=False)
        min = fnum
        max = fnum

        n = fileUtils.getFilename(file)
        orig_name = fileUtils.strFromArray(
            fileUtils.splitStringByIndex(n, return_i=None),
            0,
            -2,
        )

        for f_name in fileUtils.filterFileDirByExt(file):

            fnum = mediaUtils.getFrameNumber(f_name)
            base_n = fileUtils.strFromArray(
                fileUtils.splitStringByIndex(f_name, return_i=None), 0, -2
            )

            if fnum and orig_name == base_n:

                if int(fnum) < int(min):
                    min = fnum

                elif int(fnum) > int(max):
                    max = fnum

        return [min, max]

    @lru_cache(maxsize=None)
    def loadSequence(self, file, fps, threaded=True, wait_for_load=True) -> dict:
        if "#" in file:
            file = mediaUtils.figureHashSequenceName(file)

        self._fileChecks(file)
        f_range = self.seqRangeFromFile(file)
        tfile = mediaUtils.getSeqTemplatePath(file)
        self.setUp(file, fps, f_range)
        t_list = []
        self.is_seq = True
        t_pool = ThreadPool(10)
        for i in range(int(f_range[1]) + 1 - int(f_range[0])):

            fn = str(int(f_range[0]) + i).zfill(len(f_range[1]))

            if threaded:
                if wait_for_load:
                    t_pool.apply(
                        self._threadReadImage,
                        [
                            fn,
                            tfile.replace("#" * len(f_range[1]), fn),
                        ],
                    )
                else:
                    t_pool.apply_async(
                        self._threadReadImage,
                        [
                            fn,
                            tfile.replace("#" * len(f_range[1]), fn),
                        ],
                    )

            else:
                self.seq_images[int(fn)] = self.readImage(
                    tfile.replace("#" * len(f_range[1]), fn)
                )

        return self.seq_images

    def _threadReadImage(self, fn, file) -> list:
        self.seq_images[int(fn)] = self.readImage(file)

        if self.image_loaded_signal:
            self.image_loaded_signal.emit(fn)

    @lru_cache(maxsize=None)
    def readImage(self, file) -> dict:
        size = fileUtils.getFileSize(file)
        memory.checkMemoryFit(
            size, memory.getFreeMemorySize() * self.memory_allowed_usage
        )
        image = cv2.imread(file, cv2.IMREAD_UNCHANGED)

        return image

    @lru_cache(maxsize=None)
    def loadImage(self, file) -> dict:
        fileUtils.isFile(file)
        mediaUtils.isMedia(file)

        self.setUp(file, self.fps, [0, 0])
        self.seq_images[0] = self.readImage(file)

        if self.image_loaded_signal:
            self.image_loaded_signal.emit(0)

        return self.seq_images

    def setUp(self, file, fps, full_frange) -> None:
        self.name = fileUtils.getFilename(fileUtils.formatFilepath(file))
        self.file = file
        self.fps = fps

        if self.full_frange == [0, 0]:
            self.full_frange = full_frange

        self.getFpsConstant()

    def getFpsConstant(self) -> float:
        self.fps_constant = float(1) / self.fps
        return self.fps_constant

    def offload(self, frame_number=None) -> None:
        if frame_number:
            self.seq_images.pop(frame_number, None)
            # del self.seq_images[frame_number]
            return

        self.seq_images = {}

    def reload(self, frame_number=None) -> None:
        if frame_number:
            f_file = mediaUtils.getSeqTemplatePath(self.file)
            fn = str(frame_number).zfill(len(self.full_frange[1]))
            f_file = f_file.replace("#" * len(self.full_frange[1]), fn)
            self.seq_images[frame_number] = self.readImage(f_file)
            return

        if self.is_seq:
            self.loadSequence(self.file, self.fps)
            return

        self.loadImage(self.file)
        return


# corrections
