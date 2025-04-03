import os
import glob
from utils.constants import SPRITES_PATH, EMOTION_TO_DURATION_MS
from PyQt6 import QtWidgets, QtGui, QtCore

class AvatarAnimator(QtCore.QObject):
    def __init__(self, label: QtWidgets.QLabel, parent=None):
        super().__init__(parent)
        self.label = label  # QLabel, в который будет вставляться QPixmap
        self.frames = []
        self.frame_index = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)

    def start_animation(self, mood: str):
        folder = os.path.join(SPRITES_PATH, mood)
        if not os.path.isdir(folder):
            print(f"[⚠] Папка с эмоцией не найдена: {folder}")
            return

        png_files = sorted(glob.glob(os.path.join(folder, "*.png")))
        if not png_files:
            print(f"[⚠] Нет PNG-файлов в: {folder}")
            return

        self.frames = [QtGui.QPixmap(f) for f in png_files]
        self.frame_index = 0
        duration = EMOTION_TO_DURATION_MS.get(mood, 200)
        self.timer.setInterval(duration)
        self.timer.start()

        # Установим первый кадр сразу
        self.label.setPixmap(self.frames[0])
        self.label.setScaledContents(True)

    def update_frame(self):
        if not self.frames:
            return

        pixmap = self.frames[self.frame_index]
        self.label.setPixmap(pixmap)
        self.frame_index = (self.frame_index + 1) % len(self.frames)

    def stop(self):
        self.timer.stop()
        self.frames.clear()