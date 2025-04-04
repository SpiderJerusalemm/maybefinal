from PyQt6 import QtWidgets, QtGui, QtCore
import os
from core.avatar_animator import AvatarAnimator
from core.gpt_bridge import send_message_to_chatgpt
from core.worker import GPTWorker
from core.gpt_bridge import init_selenium_connection

# Стартовая эмоция
DEFAULT_EMOTION = "neutral"
SPRITES_PATH = f"C:/Users/user/Music/project/amadeus_emotion/{DEFAULT_EMOTION}"

class PhoneModeExpanded(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(361, 728)

        self.old_pos = None
        self.bot_mood = "neutral"
        self.driver = init_selenium_connection()
        

        # 📱 Фон телефона
        phone_bg = QtGui.QPixmap("C:/Users/user/Music/project/phone_layout.png")
        self.background = QtWidgets.QLabel(self)
        self.background.setPixmap(phone_bg)
        self.background.setScaledContents(True)
        self.background.setGeometry(0, 0, 361, 728)

        # 🧠 Аватар
        self.avatar_label = QtWidgets.QLabel(self)
        self.avatar_label.setGeometry(17, 63, 330, 550)
        self.avatar_label.setStyleSheet("background-color: transparent; border: none;")
        self.avatar_label.setScaledContents(True)

        # ⚙️ Аниматор
        self.avatar_animator = AvatarAnimator(self.avatar_label)
        self.avatar_animator.start_animation(DEFAULT_EMOTION)

        # 💬 Ответ нейросети
        self.response_area = QtWidgets.QTextBrowser(self)
        self.response_area.setGeometry(32, 420, 298, 180)
        self.response_area.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            color: #e6dbc8;
            font-family: 'Courier New';
            font-size: 12px;
            border-radius: 8px;
            padding: 6px;
        """)

        self.toggle_input_button = QtWidgets.QPushButton(self)
        self.toggle_input_button.setGeometry(62, 613, 46, 45)  # Кнопка внизу телефона
        self.toggle_input_button.setText("")  # Можно заменить иконкой
        self.toggle_input_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);  /* Едва заметный эффект при наведении */
            }
        """)
        self.toggle_input_button.clicked.connect(self.toggle_input_panel)


        # 📥 Панель ввода (будет появляться поверх нижней части экрана)
        self.bottom_input_panel = QtWidgets.QWidget(self)
        self.bottom_input_panel.setGeometry(30, 635, 300, 80)  # внутри окна!
        self.bottom_input_panel.setStyleSheet("background-color: rgba(20, 20, 20, 180); border-radius: 8px;")
        self.bottom_input_panel.hide()

        layout = QtWidgets.QVBoxLayout(self.bottom_input_panel)
        layout.setContentsMargins(8, 8, 8, 8)
        self.hidden_input = QtWidgets.QLineEdit()
        self.hidden_input.setPlaceholderText("Введите сообщение...")
        self.hidden_input.setStyleSheet("color: white; background-color: #222; padding: 6px; border-radius: 4px;")
        layout.addWidget(self.hidden_input)


        # 📨 Кнопка отправки
        self.send_button = QtWidgets.QPushButton(self)
        self.send_button.setGeometry(158, 613, 46, 45)
        self.send_button.setText("")  # Без текста
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);  /* Едва заметный эффект при наведении */
            }
        """)
        self.send_button.clicked.connect(self.on_send_clicked)
        

    def on_send_clicked(self):
        user_text = self.hidden_input.text().strip()
        if not user_text:
            return

        self.response_area.append(f"<b>Вы:</b> {user_text}")
        self.hidden_input.clear()

        self.worker = GPTWorker(user_text, self.bot_mood, self.driver)
        self.worker.response_ready.connect(self.handle_gpt_response)
        self.worker.start()

    # 🖱️ Перетаскивание
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def toggle_input_panel(self):
        if self.bottom_input_panel.isVisible():
            self.bottom_input_panel.hide()
        else:
            self.bottom_input_panel.show()

    def handle_gpt_response(self, text, mood):
        self.response_area.append(f"<b>Курису:</b> {text}")

        if mood != self.bot_mood:
            self.bot_mood = mood
            self.avatar_animator.start_animation(mood)