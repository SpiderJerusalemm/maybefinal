from PyQt6 import QtWidgets, QtGui, QtCore

class GPTWorker(QtCore.QThread):
    response_ready = QtCore.pyqtSignal(str, str)  # текст, эмоция

    def __init__(self, message, mood):
        super().__init__()
        self.message = message
        self.mood = mood

    def run(self):
        try:
            from core.gpt_bridge import send_message_to_chatgpt
            response, emotion = send_message_to_chatgpt(self.message, self.mood)
            self.response_ready.emit(response, emotion)
        except Exception as e:
            print(f"[GPTWorker ERROR] {e}")
            self.response_ready.emit("(Ошибка связи с GPT)", "neutral")