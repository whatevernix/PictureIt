import os, sys


def isFile(file) -> None:
    if not os.path.exists(file):
        raise ValueError("Can't find %s File." % file)

    if os.path.isdir(file):
        raise ValueError("File is Requested, While %s Was Given." % file)


def getExtension(file) -> str:
    ext = file.split(os.extsep)[-1]
    return ext


def formatFilepath(file) -> str:
    return file.replace("\\", "/")


def getFilename(file) -> str:
    file = formatFilepath(file)
    return file.split("/")[-1]


def splitStringByIndex(file_name, return_i=-2, split_str=".") -> list:
    s = file_name.rsplit(split_str)

    if return_i == None:
        return s

    compare = abs(return_i)

    if len(s) > compare:
        return s[return_i]

    return None


def strFromArray(str_array, i_start=0, i_end=-1, split_str=".") -> str:
    s_out = str_array[i_start]

    for s in str_array[i_start + 1 : i_end]:
        s_out = s_out + split_str + s

    return s_out


def filterFileDirByExt(file) -> list:
    filteredFiles = []
    files = os.listdir(os.path.dirname(file))
    ext = getExtension(file)

    for c in files:
        if c[-len(ext) :] == ext:
            filteredFiles.append(c)

    return filteredFiles


def getFileSize(file) -> int:
    return os.path.getsize(file)


def getVariableSize(variable, in_MB=False) -> int:
    if in_MB:
        return sys.getsizeof(variable) >> 20
    return sys.getsizeof(variable)
