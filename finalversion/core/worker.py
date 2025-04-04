from PyQt6 import QtWidgets, QtGui, QtCore
import sys

class GPTWorker(QtCore.QThread):
    response_ready = QtCore.pyqtSignal(str, str)  # текст, эмоция

    def __init__(self, message, mood, driver):
        super().__init__()
        self.message = message
        self.mood = mood
        self.driver = driver

    def run(self):
        try:
            if self.driver is None:
                raise RuntimeError("❌ WebDriver (driver) не инициализирован!")

            from core.gpt_bridge import send_message_to_chatgpt
            print("[DEBUG] Отправка в GPT:", self.message[:100])
            response, emotion = send_message_to_chatgpt(self.driver, self.message, self.mood)
            self.response_ready.emit(response, emotion)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.response_ready.emit("(Ошибка связи с GPT)", "neutral")