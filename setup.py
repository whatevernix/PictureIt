import platform
from setuptools import setup

_platform = platform.system()

if _platform == "Windows":
    import py2exe

    extra_options = dict(setup_requires=["py2exe"], console=["main.py"])

elif _platform == "Darwin":  # not working on m1
    import py2app

    extra_options = dict(
        setup_requires=["py2app"],
        app=["main.py"],
        options=dict(py2app=dict(argv_emulation=False)),
    )
else:  # not tested
    import py2app

    extra_options = dict(
        scripts=["main.py"],
    )
print(extra_options)
setup(name="JosefPlayer", **extra_options)


# Windows# python setup.py py2exe
# macOS# python setup.py py2app
# exe path - D:\Sync\Codejects\VfxImage\PictureIt\dist\main.exe
# exe test - D:\Sync\Codejects\VfxImage\PictureIt\dist\main.exe C:\Users\simaj\OneDrive\Documents\maya\projects\default\images\test.#.jpg
# pyinstaller --onefile --paths="D:/Sync/Codejects/VfxImage/PictureIt/venv/Lib/python3.8/site-packages/cv2/python-3.8" main.py
