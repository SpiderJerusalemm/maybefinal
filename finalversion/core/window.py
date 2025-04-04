import os
from PyQt6 import QtWidgets, QtGui, QtCore

from core.background import BackgroundWidget
from core.avatar_animator import AvatarAnimator
from core.gpt_bridge import init_selenium_connection, send_message_to_chatgpt
from utils.constants import SPRITE_RATIO
from utils.constants import EMOTION_TO_DURATION_MS
from core.fonts import load_custom_fonts

class BaseLayoutWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(960, 600)

        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))

        self.setObjectName("MainWindow")
        self.setStyleSheet("""
            QTextEdit, QTextBrowser {
                background-color: rgba(36, 31, 28, 0.88);
                border: 1px solid #3d352f;
                color: #e6dbc8;
                font-family: 'SteinsGateFont', 'Courier New', monospace;  /* <-- кастомный + fallback */
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

        custom_font_family = load_custom_fonts()

        # Применим кастомный шрифт глобально
        font = QtGui.QFont(custom_font_family, 12)
        QtWidgets.QApplication.setFont(font)

        # Подключение к GPT через Selenium
        self.driver = init_selenium_connection()

        # Текущее настроение
        self.current_mood = "neutral"

        self.build_ui()

    def build_ui(self):
        container = QtWidgets.QWidget()
        self.setCentralWidget(container)

        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.background = BackgroundWidget()
        layout.addWidget(self.background)

        foreground = QtWidgets.QWidget(self.background)
        foreground.setGeometry(0, 0, self.width(), self.height())
        self.background.resizeEvent = lambda event: foreground.setGeometry(0, 0, self.background.width(), self.background.height())

        main_layout = QtWidgets.QVBoxLayout(foreground)
        main_layout.setContentsMargins(20, 20, 20, 20)

        h_center = QtWidgets.QHBoxLayout()
        h_center.addStretch(1)

        # Центрированный контейнер
        center = QtWidgets.QWidget()
        center.setMinimumSize(720, 480)
        center.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        h_center.addWidget(center)
        h_center.addStretch(1)
        main_layout.addLayout(h_center)

        center_layout = QtWidgets.QHBoxLayout(center)
        center_layout.setContentsMargins(16, 16, 16, 16)
        center_layout.setSpacing(20)

        # Аватар
        avatar_container = QtWidgets.QVBoxLayout()
        avatar_container.addStretch(1)

        self.avatar_label = QtWidgets.QLabel()
        self.avatar_label.setObjectName("AvatarLabel")
        self.avatar_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setScaledContents(True)
        self.avatar_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        avatar_holder = QtWidgets.QWidget()
        avatar_layout = QtWidgets.QVBoxLayout(avatar_holder)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.addWidget(self.avatar_label)

        avatar_container.addWidget(avatar_holder)
        avatar_container.addStretch(1)
        center_layout.addLayout(avatar_container)

        # Анимация
        self.animator = AvatarAnimator(self.avatar_label)
        self.animator.start_animation("neutral")

        # Чат и ввод
        chat_layout = QtWidgets.QVBoxLayout()
        chat_layout.setSpacing(12)

        self.chat_browser = QtWidgets.QTextBrowser()
        self.chat_browser.setPlaceholderText("История сообщений...")
        self.chat_browser.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        chat_layout.addWidget(self.chat_browser)

        self.input_field = QtWidgets.QTextEdit()
        self.input_field.setFixedHeight(64)
        self.input_field.setPlaceholderText("Введите сообщение...")
        chat_layout.addWidget(self.input_field)

        self.send_button = QtWidgets.QPushButton("Отправить")
        self.send_button.setFixedHeight(36)
        self.send_button.clicked.connect(self.on_send_message)
        chat_layout.addWidget(self.send_button)

        center_layout.addLayout(chat_layout, 2)

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def on_send_message(self):
        user_text = self.input_field.toPlainText().strip()
        if not user_text:
            return

        self.chat_browser.append(f"<b>Вы:</b> {user_text}")
        reply, new_mood = send_message_to_chatgpt(self.driver, user_text, self.current_mood)
        self.chat_browser.append(f"<b>Курису:</b> {reply}")
        self.input_field.clear()

        if new_mood != self.current_mood:
            self.current_mood = new_mood
            self.animator.start_animation(new_mood)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Пропорции из constants
        height = self.centralWidget().height()
        max_avatar_height = int(height * 0.8)
        max_avatar_width = int(max_avatar_height * SPRITE_RATIO)

        self.avatar_label.setMaximumSize(max_avatar_width, max_avatar_height)
        self.avatar_label.setMinimumSize(max_avatar_width, max_avatar_height)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()
        elif event.key() == QtCore.Qt.Key.Key_F1 and hasattr(self, 'controller'):
            self.controller.switch_to_compact()

    def showEvent(self, event):
        super().showEvent(event)
        self.showFullScreen()