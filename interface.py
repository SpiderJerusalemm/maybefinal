import sys
import os
from PyQt6 import QtWidgets, QtGui, QtCore

SPRITES_PATH = "C:/Users/user/Music/project/amadeus_emotion/neutral"

class BackgroundWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background_path = "C:/Users/user/Music/project/finalversion/background.png"

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pixmap = QtGui.QPixmap(self.background_path)
        scaled_pixmap = pixmap.scaled(self.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding, QtCore.Qt.TransformationMode.SmoothTransformation)
        x = (self.width() - scaled_pixmap.width()) // 2
        y = (self.height() - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)

class BaseLayoutWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        # 🚫 Минимальный размер окна, чтобы всё не сжималось
        self.setMinimumSize(960, 600)

        # 🪟 Начальный размер (можно изменить под экран)
        screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
        initial_width = min(1280, screen_geometry.width() * 0.8)
        initial_height = min(800, screen_geometry.height() * 0.8)
        self.resize(int(initial_width), int(initial_height))

        # 🪄 Центрируем окно на экране при запуске
        frame_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        self.setObjectName("MainWindow")
        self.setStyleSheet("""
            QTextEdit, QTextBrowser {
                background-color: rgba(36, 31, 28, 0.88);
                border: 1px solid #3d352f;
                color: #e6dbc8;
                font-family: 'Courier New';
                font-size: 14px;
                padding: 6px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #3d352f;
                border: 1px solid #5c5148;
                color: #d8cbbb;
                padding: 6px 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #574c42;
            }
            QLabel#AvatarLabel {
                border: 2px solid #4a4037;
                background-color: #2a2522;
            }
        """)

        container = QtWidgets.QWidget()
        self.setCentralWidget(container)

        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.background = BackgroundWidget()
        layout.addWidget(self.background)

        foreground = QtWidgets.QWidget(self.background)
        foreground.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        foreground.setGeometry(0, 0, self.width(), self.height())
        foreground.raise_()

        self.background.resizeEvent = lambda event: foreground.setGeometry(0, 0, self.background.width(), self.background.height())

        # 🔲 Основной layout поверх фона
        main_layout = QtWidgets.QVBoxLayout(foreground)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        horizontal_center = QtWidgets.QHBoxLayout()
        horizontal_center.setContentsMargins(0, 0, 0, 0)
        horizontal_center.addStretch(1)

        # 📦 Центральный контейнер
        center_container = QtWidgets.QWidget()
        center_container.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        # Вычисляем пропорциональный размер (например, 70% ширины и до 90% высоты)
        screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        max_width = int(screen_width * 0.72)
        max_height = int(screen_height * 0.88)

        center_container.setMaximumWidth(max_width)
        center_container.setMaximumHeight(max_height)
        center_container.setMinimumSize(720, 480)  # фиксируем минимальный размер

        horizontal_center.addWidget(center_container)
        horizontal_center.addStretch(1)

        # ⬇️ Вставляем центрированный горизонтальный layout внутрь основного вертикального
        main_layout.addLayout(horizontal_center)

        # 📐 Внутренний layout с аватаром и чатом
        center_layout = QtWidgets.QHBoxLayout(center_container)
        center_layout.setContentsMargins(16, 16, 16, 16)
        center_layout.setSpacing(20)

        # 🎭 Левая панель — анимированный аватар
        avatar_panel = QtWidgets.QVBoxLayout()
        avatar_panel.setContentsMargins(0, 0, 0, 0)
        avatar_panel.addStretch(1)

        # Контейнер под QLabel с аватаром
        avatar_label_container = QtWidgets.QWidget()
        avatar_label_layout = QtWidgets.QVBoxLayout(avatar_label_container)
        avatar_label_layout.setContentsMargins(0, 0, 0, 0)

        self.avatar_label = QtWidgets.QLabel()
        self.avatar_label.setObjectName("AvatarLabel")
        self.avatar_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setScaledContents(True)
        self.avatar_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        avatar_label_layout.addWidget(self.avatar_label)
        avatar_panel.addWidget(avatar_label_container)
        avatar_panel.addStretch(1)

        center_layout.addLayout(avatar_panel)

        # 🪟 Правая панель — чат и ввод
        right_panel = QtWidgets.QVBoxLayout()
        right_panel.setSpacing(12)

        self.chat_browser = QtWidgets.QTextBrowser()
        self.chat_browser.setPlaceholderText("История сообщений...")
        self.chat_browser.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        right_panel.addWidget(self.chat_browser, 8)

        self.input_field = QtWidgets.QTextEdit()
        self.input_field.setFixedHeight(64)
        self.input_field.setPlaceholderText("Введите сообщение...")
        right_panel.addWidget(self.input_field, 1)

        self.send_button = QtWidgets.QPushButton("Отправить")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFixedHeight(36)
        right_panel.addWidget(self.send_button, 0)

        center_layout.addLayout(right_panel, 2)


        self.frames = self.load_sprites()
        self.frame_index = 0

        if self.frames:
            self.avatar_label.setPixmap(self.frames[0])  # ✅ Первый кадр

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(300)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        sprite_ratio = 768 / 1276  # ≈ 0.6025

        center_height = self.centralWidget().height()
        max_avatar_height = int(center_height * 0.8)
        max_avatar_width = int(max_avatar_height * sprite_ratio)

        self.avatar_label.setMaximumSize(max_avatar_width, max_avatar_height)
        self.avatar_label.setMinimumSize(max_avatar_width, max_avatar_height)

    def load_sprites(self):
        files = sorted([os.path.join(SPRITES_PATH, f) for f in os.listdir(SPRITES_PATH) if f.endswith(".png")])
        return [QtGui.QPixmap(f) for f in files]

    
    def next_frame(self):
        if not self.frames:
            return
        self.avatar_label.setPixmap(self.frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(self.frames)

    def send_message(self):
        user_text = self.input_field.toPlainText().strip()
        if not user_text:
            return
        self.chat_browser.append(f"<b>Вы:</b> {user_text}")

        reply = "Хм. Даже ты способен на что-то осмысленное?"
        self.chat_browser.append(f"<b>Курису:</b> {reply}")
        self.input_field.clear()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()

    def showEvent(self, event):
        super().showEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = BaseLayoutWindow()
    window.showFullScreen()
    sys.exit(app.exec())