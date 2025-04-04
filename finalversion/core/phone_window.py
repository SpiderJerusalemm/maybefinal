from PyQt6 import QtWidgets, QtGui, QtCore
import os
import pytesseract
import re
from PIL import ImageGrab, Image
from core.ocr_scanner import capture_screen_text
from core.avatar_animator import AvatarAnimator
from core.gpt_bridge import send_message_to_chatgpt
from core.worker import GPTWorker
from core.gpt_bridge import init_selenium_connection

# Стартовая эмоция
DEFAULT_EMOTION = "neutral"
SPRITES_PATH = f"C:/Users/user/Music/project/amadeus_emotion/{DEFAULT_EMOTION}"

class PhoneModeExpanded(QtWidgets.QMainWindow):
    def __init__(self, driver, controller=None):
        super().__init__()
        self.driver = driver
        self.controller = controller

        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(361, 728)

        self.old_pos = None
        self.bot_mood = "neutral"
        

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

        #кнопка top of all
        self.always_on_top = True  # по умолчанию включено

        self.pin_button = QtWidgets.QPushButton(self)
        self.pin_button.setGeometry(300, 10, 40, 30)
        self.pin_button.setText("📍")  # активная булавка
        self.pin_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 120);
                border: 1px solid #666;
                border-radius: 6px;
                font-size: 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 40);
            }
        """)
        self.pin_button.clicked.connect(self.toggle_always_on_top)

        #кнопка скана
        self.scan_button = QtWidgets.QPushButton(self)
        self.scan_button.setGeometry(252, 10, 40, 30)
        self.scan_button.setText("🔍")
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 120);
                border: 1px solid #666;
                border-radius: 6px;
                font-size: 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 255, 40);
            }
        """)
        self.scan_button.clicked.connect(self.run_ocr_capture)


        self.last_clipboard_image = None
        self.clipboard_timer = QtCore.QTimer()
        self.clipboard_timer.timeout.connect(self.check_clipboard_image)
        self.clipboard_timer.start(2000)   # каждые 2 секунды
        

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
        self.type_text(text)  # печатает по буквам

        if mood != self.bot_mood:
            self.bot_mood = mood
            self.avatar_animator.start_animation(mood)

    def type_text(self, full_text):
        self.typed_text = ""
        self.full_text = full_text
        self.char_index = 0

        self.response_area.setHtml("<b>Курису:</b><br>")
        
        self.typing_timer = QtCore.QTimer()
        self.typing_timer.timeout.connect(self.update_typed_text)
        self.typing_timer.start(30)  # Задержка между буквами (мс)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_F1 and self.controller:
            self.controller.switch_to_main()

    def update_typed_text(self):
        if self.char_index < len(self.full_text):
            self.typed_text += self.full_text[self.char_index]
            self.char_index += 1
            self.response_area.setHtml(f"<b>Курису:</b><br>{self.typed_text}")
            self.response_area.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        else:
            self.typing_timer.stop()

    def toggle_always_on_top(self):
        if self.always_on_top:
            # Отключаем "поверх всех"
            self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, False)
            self.always_on_top = False
            self.pin_button.setText("📌")  # неактивная булавка
        else:
            # Включаем "поверх всех"
            self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, True)
            self.always_on_top = True
            self.pin_button.setText("📍")  # активная булавка

        self.show()  # нужно вызвать для применения новых флагов

    def capture_clipboard_and_ask_gpt(self):
        self.response_area.append("<i>📋 Анализ буфера...</i>")
        from core.gpt_bridge import send_message_to_chatgpt
        from core.ocr_scanner import capture_clipboard_text

        text = capture_clipboard_text()

        if not text:
            self.response_area.append("<i>❌ В буфере нет текста или изображения</i>")
            return

        self.response_area.append(f"<b>📷 Распознано:</b><br>{text}")

        # Отправляем в GPT через поток
        self.worker = GPTWorker(text, self.bot_mood, self.driver)
        self.worker.response_ready.connect(self.handle_gpt_response)
        self.worker.start()

    def run_ocr_capture(self):
        self.response_area.append("<i>🔍 Сканирование экрана...</i>")
        text = capture_screen_text()

        if text:
            self.response_area.append(f"<b>🧠 Распознанный текст:</b><br>{text}")
        else:
            self.response_area.append("<i>❌ Текст не найден</i>")

    
    def monitor_clipboard_for_image(self):
        try:
            image = ImageGrab.grabclipboard()
            if not isinstance(image, Image.Image):
                return

            image = image.convert("RGB")
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            text = pytesseract.image_to_string(image, lang='eng+rus')
            text = re.sub(r"[\x00-\x1F]+", " ", text).strip()

            if text:
                self.response_area.append(f"<b>📷 Распознано:</b><br>{text}")
                
                self.worker = GPTWorker(text, self.bot_mood, self.driver)
                self.worker.response_ready.connect(self.handle_gpt_response)
                self.worker.start()
            else:
                self.response_area.append("<i>❌ Текст не найден</i>")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.response_area.append(f"<i>❌ Ошибка при анализе буфера:<br>{str(e)}</i>")


    def check_clipboard_image(self):
        try:
            import PIL

            data = ImageGrab.grabclipboard()
            if isinstance(data, Image.Image):
                print("[DEBUG] Найдено изображение в буфере:", data.size)
                # обрабатываем
            elif data is None:
                pass  # ничего не пишем — это нормально
            else:
                print("[DEBUG] В буфере не изображение:", type(data))

        except Exception as e:
            print("[ERROR] Ошибка в check_clipboard_image:")
            import traceback
            traceback.print_exc()