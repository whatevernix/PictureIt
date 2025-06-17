import src
from src import core
from src.utils import fileUtils
from src.ui import playerWindow
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QMainWindow,
    QGraphicsOpacityEffect,
)
from PyQt6.QtGui import QPixmap, QColor, QImage, QIcon
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal, QPropertyAnimation, QParallelAnimationGroup
import sys, os, time, threading


class MainWindow(QMainWindow):
    frame_changed_signal = pyqtSignal(object)
    image_loaded_signal = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = playerWindow.Ui_MediaPlayer()
        self.play_icon = QIcon()
        self.cw_w = self.frameGeometry().width()
        self.cw_h = self.frameGeometry().height()
        self.play_icon.addPixmap(
            QPixmap("src/ui/gui/btn_play.png"), QIcon.Mode.Active, QIcon.State.On
        )
        self.pause_icon = QIcon()
        self.pause_icon.addPixmap(
            QPixmap("src/ui/gui/btn_pause.png"), QIcon.Mode.Active, QIcon.State.On
        )
        self.ui.setupUi(self)
        self.Core = core.Core(self.frame_changed_signal, self.image_loaded_signal)
        self.Core.current_image = core.media.mediaUtils.generateBlankFrame(512, 256)
        self.ui.l_image.setScaledContents = True
        self._size = [512, 512]
        self.is_converting = False
        sys_args = []
        if len(sys.argv) > 1:
            sys_args = sys.argv[1:]

        if sys_args:
            try:
                self.loadMedia(sys_args[0], sys_args[1], True)
            except:
                self.loadMedia(sys_args[0], 25, True)
            else:
                pass

    def setupControl(self):
        self.frame_changed_signal.connect(self.updatePreviewEvent)
        self.ui.btn_play_pause.clicked.connect(self.playStopEvent)
        self.ui.horizontalSlider.valueChanged.connect(self.changeTimelineFrameEvent)
        self.ui.box_frame.valueChanged.connect(self.frameBoxEvent)
        self.ui.box_fps.valueChanged.connect(self.fpsBoxEvent)
        self.image_loaded_signal.connect(self.convertToQImageSequenceEvent)

    # ---------------------------------------- Animations -------------------------------------------
    def hideWidget(self, Widget):
        effect = QGraphicsOpacityEffect(Widget)
        Widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(
            Widget,
            propertyName=b"opacity",
            targetObject=effect,
            duration=1500,
            startValue=0.0,
            endValue=1.0,
        )
        anim_group = QParallelAnimationGroup()
        anim_group.addAnimation(anim)
        anim_group.start()

    def showWidget(self, Widget):
        effect = QGraphicsOpacityEffect(Widget)
        Widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(
            Widget,
            propertyName=b"opacity",
            targetObject=effect,
            duration=500,
            startValue=1.0,
            endValue=0.0,
        )
        self.anim_group2 = QParallelAnimationGroup()
        self.anim_group2.addAnimation(anim)
        self.anim_group2.start()

    # ---------------------------------------- Events -------------------------------------------
    def playStopEvent(self):
        if self.Core.is_playing:
            self.Core.is_playing = False
            self.ui.btn_play_pause.setIcon(self.play_icon)
            return

        self.Core.play()
        self.ui.btn_play_pause.setIcon(self.pause_icon)

    def fpsBoxEvent(self):
        val = self.ui.box_fps.value()
        self.Core.changeFps(val)

    def frameBoxEvent(self):
        val = self.ui.box_frame.value()
        if val >= self.Core.start_frame and val <= self.Core.end_frame:
            self.Core.current_frame = val
            self.updatePreviewEvent(update_frame_box=False)

    def resizeEvent(self, *args, **kwargs):

        is_playing = self.Core.is_playing
        self.Core.is_playing = False
        self.getWindowSize()
        self.resizeImage()
        self.fitPlaybackLayout()
        self.fitInfoLayout()
        self.updatePreviewEvent()

        if is_playing:
            self.Core.play()

    def convertToQImageSequenceEvent(self, use_threading=True):
        if use_threading:
            thread = threading.Thread(target=self._convertToQImageSequence, daemon=True)
            thread.start()
        else:
            self._convertToQImageSequence()

    def _convertToQImageSequence(self, offload=True):
        while self.is_converting:
            time.wait(0.1)

        keys = list(self.Core.Media_dic[self.Core.active_media].seq_images.keys())

        for key in keys:
            image = self.Core.Media_dic[self.Core.active_media].seq_images[key]
            self._size = [
                image.shape[0],
                image.shape[1],
            ]
            qt_image = self.createQtImage(image)
            self.Core.edited_seq[key] = qt_image

            if offload:
                self.Core.Media_dic[self.Core.active_media].offload(key)

        self.is_converting = False

    def updatePreviewEvent(self, update_timeline=True, update_frame_box=True):
        try:
            self.frame_changed_signal.disconnect()

        except:
            self.frame_changed_signal.connect(self.updatePreviewEvent)
            self.frame_changed_signal.disconnect()
        try:
            self.qt_image = self.Core.edited_seq[self.Core.current_frame]
            self.renderImage()

            if update_timeline:
                self.setTimeline()

            if update_frame_box:
                self.setFrameBox()

            self.frame_changed_signal.connect(self.updatePreviewEvent)
        except:
            pass  # logger !

    # ---------------------------------------- Media and Timeline -------------------------------------------
    def loadMedia(self, path, fps, as_sequence):
        path = path.replace("\\", "/")
        Media = self.Core.addMedia(path, as_sequence, fps, False)
        self.Core.active_media = Media.name
        self.Core.current_frame = int(Media.full_frange[0])
        self.image_scale_factor = 1
        self.ui.box_fps.setValue(fps)

        self.setTimeline()
        self.updatePreviewEvent()

    def setTimelineFrame(self):
        self.ui.horizontalSlider.blockSignals(True)
        self.ui.horizontalSlider.setValue(self.Core.current_frame)
        self.ui.horizontalSlider.blockSignals(False)

    def changeTimelineFrameEvent(self):
        self.Core.current_frame = self.ui.horizontalSlider.value()
        self.updatePreviewEvent(update_timeline=False)

    def fitPlaybackLayout(self):
        h = self.ui.playback_widget.frameGeometry().height()
        self.ui.playback_widget.setGeometry(
            QtCore.QRect(
                10,
                int(self.cw_h - (h + 50)),
                self.cw_w - 10,
                int(h),
            )
        )

    def setFrameBox(self):
        self.ui.box_frame.blockSignals(True)
        self.ui.box_frame.setValue(self.Core.current_frame)
        self.ui.box_frame.blockSignals(False)

    def setTimeline(self):
        f_range = self.Core.Media_dic[self.Core.active_media].full_frange
        self.ui.horizontalSlider.setRange(int(f_range[0]), int(f_range[1]))
        self.setTimelineFrame()

    def fitInfoLayout(self):
        self.ui.info_widget.setGeometry(
            QtCore.QRect(
                10,
                self.cw_h - 90,
                300,
                60,
            )
        )

    def getWindowSize(self):
        self.cw_w = self.frameGeometry().width()
        self.cw_h = self.frameGeometry().height()
        return self.cw_w, self.cw_h

    def renderImage(self):

        new_s = self.ui.l_image.size()

        self.ui.l_image.setPixmap(
            QPixmap.fromImage(
                self.qt_image.scaled(
                    new_s,
                    aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    transformMode=QtCore.Qt.TransformationMode.SmoothTransformation,
                )
            )
        )

    def createQtImage(self, image):

        image, qt_format = core.media.mediaUtils.prepareForDisplay(image)

        format = getattr(QImage.Format, qt_format)
        qt_image = QImage(
            image,
            image.shape[1],
            image.shape[0],
            image.strides[0],
            format,
        )
        qt_image = qt_image.rgbSwapped()

        return qt_image

    def resizeImage(self):

        h, w = self._size
        h_dif = float((self.cw_h - 110) / h)
        scale_constant = float(self.cw_w / w)
        self.image_scale_factor = scale_constant

        if h_dif < scale_constant:
            scale_constant = h_dif

        resized_w = int(w * scale_constant)
        resized_h = int(h * scale_constant)
        self.ui.l_image.setGeometry(
            QtCore.QRect(
                int((self.cw_w - resized_w) / 2),
                int(((self.cw_h - 110) - resized_h) / 2),
                resized_w,
                resized_h,
            )
        )

    def applyEdits(self):

        self.Core.editSequence(
            self.Core.Media_dic[self.Core.active_media].seq_images,
            self.edits,
        )
        self.convertToQImageSequenceEvent(from_editted=True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MWindow = MainWindow()
    MWindow.show()
    MWindow.update()
    MWindow.setupControl()
    MWindow.resizeEvent()
    sys.exit(app.exec())
