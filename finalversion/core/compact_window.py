from PyQt6 import QtWidgets, QtGui, QtCore
import sys
import os

SPRITES_PATH = "C:/Users/user/Music/project/amadeus_emotion/neutral"
PHONE_IMAGE_PATH = "C:/Users/user/Music/project/phone_layout.png"  # PNG фон телефона

class PhoneModeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AMADEUS - Phone Mode")
        self.setFixedSize(260, 520)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")

        self.central = QtWidgets.QWidget()
        self.setCentralWidget(self.central)

        layout = QtWidgets.QVBoxLayout(self.central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Фон телефона
        self.phone_background = QtWidgets.QLabel()
        self.phone_background.setPixmap(QtGui.QPixmap(PHONE_IMAGE_PATH))
        self.phone_background.setScaledContents(True)
        layout.addWidget(self.phone_background)

        # Экран аватара (накладывается поверх фона)
        self.avatar_label = QtWidgets.QLabel(self.phone_background)
        self.avatar_label.setGeometry(22, 50, 210, 160)  # координаты и размер "экрана"
        self.avatar_label.setScaledContents(True)

        # Поле ввода текста (внизу телефона)
        self.input_field = QtWidgets.QLineEdit(self.phone_background)
        self.input_field.setPlaceholderText("Введите сообщение...")
        self.input_field.setGeometry(22, 380, 160, 28)
        self.input_field.setStyleSheet("background-color: #1e1a17; color: white; border: 1px solid #3d352f;")

        self.send_button = QtWidgets.QPushButton("▶", self.phone_background)
        self.send_button.setGeometry(190, 380, 40, 28)
        self.send_button.clicked.connect(self.send_message)

        # Загружаем спрайты
        self.frames = self.load_sprites()
        self.frame_index = 0

        if self.frames:
            self.avatar_label.setPixmap(self.frames[0])

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(300)

    def load_sprites(self):
        files = sorted([os.path.join(SPRITES_PATH, f) for f in os.listdir(SPRITES_PATH) if f.endswith(".png")])
        return [QtGui.QPixmap(f) for f in files]

    def next_frame(self):
        if not self.frames:
            return
        self.avatar_label.setPixmap(self.frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(self.frames)

    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        print(f"[PHONE] Вы: {text}")
        self.input_field.clear()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PhoneModeWindow()
    window.show()
    sys.exit(app.exec())
