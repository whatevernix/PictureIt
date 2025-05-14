import os, numpy
from src.utils import fileUtils
from src.utils import configs
import cv2


_configPath = os.getcwd().replace("\\", "/") + r"/src/configs/media.yaml"
media_config = configs.yaml_open(_configPath)


def getFrameNumber(file_name, silent=True) -> str:
    value = fileUtils.splitStringByIndex(file_name)
    if value and value.isdigit():
        return value

    if silent:
        return

    raise ValueError("File Name %s Does not Follow name.frame.ext format" % file_name)


def resizeImage(image, width, height) -> list:
    return cv2.resize(image, [width, height])


def figureHashSequenceName(file) -> str:
    orig_name = fileUtils.strFromArray(
        fileUtils.splitStringByIndex(file, return_i=None), 0, -2
    ).split("/")[-1]
    path = file.replace(file.split("/")[-1], "")
    str_orig_fn = fileUtils.splitStringByIndex(file, return_i=-2)

    for f_name in fileUtils.filterFileDirByExt(file):

        fnum = getFrameNumber(f_name)
        base_n = fileUtils.strFromArray(
            fileUtils.splitStringByIndex(f_name, return_i=None), 0, -2
        )
        str_fn = fileUtils.splitStringByIndex(f_name, return_i=-2)

        if fnum and orig_name == base_n:  # and len(str_orig_fn) == len(str_fn)
            return path + f_name

    return file


def isMediaObject(object) -> bool:
    if type(object).__name__ == "Media":
        return True
    else:
        raise ValueError("%s is not Media Type Class." % object)


def isMedia(file) -> bool:
    ext = fileUtils.getExtension(file)
    if ext in media_config["FileTypes"]["Accepted"]:
        return True

    raise ValueError("%s is Not Supported Media." % file)


def getSeqTemplatePath(file) -> str:
    fname = fileUtils.getFilename(file)
    getFrameNumber(fname, silent=False)  # used as check

    sname = fileUtils.splitStringByIndex(fname, None)
    sname[-2] = "#" * len(sname[-2])
    hname = sname[0]

    for s in sname[1:]:
        hname = hname + "." + s

    return file.replace(fname, hname)


def generateBlankFrame(width, height) -> list:
    return numpy.zeros(shape=[height, width, 3], dtype=numpy.uint8)


def getFrameNumber(file_name, silent=True) -> int:
    value = fileUtils.splitStringByIndex(file_name)
    if value and value.isdigit():
        return value

    if silent:
        return

    raise ValueError("File Name %s Does not Follow name.frame.ext format" % file_name)


def generateCheckerboard(w, h, sq=20):
    pix = numpy.zeros((w, h, 3), dtype=numpy.uint8)
    # Make a checkerboard
    row = [[(0x99, 0x99, 0x99), (0xAA, 0xAA, 0xAA)][(i // sq) % 2] for i in range(w)]
    pix[[i for i in range(h) if (i // sq) % 2 == 0]] = row
    row = [[(0xAA, 0xAA, 0xAA), (0x99, 0x99, 0x99)][(i // sq) % 2] for i in range(w)]
    pix[[i for i in range(h) if (i // sq) % 2 == 1]] = row
    return pix


def prepareForDisplay(image, gamma=2) -> dict:
    for dtype in media_config["FileTypes"]["NormalizeTypes"]:
        if image.dtype == dtype:
            image = image ** (1 / gamma)
            # null = numpy.zeros(image.shape)
            # image = cv2.normalize(image, null, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            break

    qt_format = media_config["DisplayFormats"][str(image.dtype)][0]

    if image.shape[2] == 4:
        qt_format = media_config["DisplayFormats"][str(image.dtype)][1]

    return image, qt_format
