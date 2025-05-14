import psutil


def getWholeMemorySize():
    return psutil.virtual_memory().total


def getUsedMemorySize():
    return psutil.virtual_memory().used


def getFreeMemorySize():
    return psutil.virtual_memory().free


def checkMemoryFit(filesize, memory_free):
    if filesize <= memory_free:
        return True
    raise MemoryError("Memory Limit Reached.")
