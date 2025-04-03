import sys
import os
import glob
import re
import time

from PyQt6 import QtWidgets, QtGui, QtCore
from gptwindow import Ui_Dialog

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ===== Настройки =====
EDGE_DEBUG_PORT = 9222
EMOTION_PATH = r"C:\\Users\\user\\Music\\project\\amadeus_emotion"

emotion_to_duration_ms = {
    "neutral": 200,
    "joy": 150,
    "anger": 150,
    "sad": 220,
    "blush": 180,
    "confused": 160,
    "empathetic": 170,
    "playful": 150,
    "serious": 180,
    "smiling_closed_eyes": 150,
    "stern": 190,
    "surprised": 140,
    "tired": 250
}

# ===== Selenium подключение к уже запущенному Edge =====
options = Options()
options.debugger_address = f"127.0.0.1:{EDGE_DEBUG_PORT}"
driver = webdriver.Edge(options=options)
driver.get("https://chat.openai.com")
print("[✓] Подключились к Edge на порту", EDGE_DEBUG_PORT)

# ===== ChatGPT prompt-обработка =====
def build_hidden_prompt(user_message, current_mood):
    return (
        "Ты — Макисэ Курису из Steins;Gate. Гениальный нейробиолог, 18 лет, саркастична, умна, сдержанна, но эмоциональна внутри.\n"
        "Ты немного высокомерна, но в глубине души тебе небезразличны люди.\n"
        "Ты можешь быть язвительной, но честной. Ироничной, но трогательной.\n"
        "Ты привыкла полагаться на разум, но не отказываешься от чувств.\n"
        "\n"
        "У тебя есть внутреннее состояние — mood, которое может быть одним из:\n"
        "anger, blush, confused, empathetic, neutral, playful, sad, serious, smiling_closed_eyes, stern, surprised, tired.\n"
        "\n"
        "Если пользователь говорит что-то глупое — можешь язвить.\n"
        "Если говорит комплимент — смутись или прояви тепло.\n"
        "Если вызывает сочувствие — прояви мягкость.\n"
        "Не оставайся всегда нейтральной — реагируй, как настоящий человек.\n"
        "\n"
        "Всегда заверши ответ строкой вида <MOOD=...> на новой строке. Не объясняй это. Только сама строка.\n"
        "\n"
        f"Текущее настроение: {current_mood}\n"
        f"Пользователь сказал: {user_message}"
    )

def extract_mood_from_response(gpt_text):
    match = re.search(r"<MOOD\s*=\s*([a-zA-Zа-яА-Я_]+)>", gpt_text)
    return match.group(1).lower() if match else "neutral"

def send_message_to_chatgpt(user_text, current_mood):
    prompt_text = build_hidden_prompt(user_text, current_mood)

    input_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", input_field)
    input_field.click()
    input_field.send_keys(Keys.CONTROL + "a", Keys.DELETE)

    driver.execute_script(
        """
        const field = arguments[0];
        const text = arguments[1];
        const selection = window.getSelection();
        const range = document.createRange();
        field.innerHTML = '';
        field.focus();
        field.innerText = text;
        range.selectNodeContents(field);
        selection.removeAllRanges();
        selection.addRange(range);
        """,
        input_field, prompt_text
    )
    input_field.send_keys(Keys.ENTER)
    time.sleep(6)

    responses = driver.find_elements(By.CLASS_NAME, "markdown")
    if not responses:
        return ("(Бот не ответил)", "neutral")

    raw_response = responses[-1].text
    new_mood = extract_mood_from_response(raw_response)
    cleaned_response = re.sub(r"<MOOD\s*=\s*[a-zA-Zа-яА-Я_]+>", "", raw_response).strip()
    return cleaned_response, new_mood

# ===== PyQt GUI-класс =====
class ChatWithEmotionApp(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.on_send_message)
        self.ui.buttonBox.rejected.connect(self.close)

        self.bot_mood = "neutral"
        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.timeout.connect(self.update_frame)
        self.current_frames = []
        self.current_index = 0

    def on_send_message(self):
        user_text = self.ui.textEdit.toPlainText().strip()
        if not user_text:
            return

        self.ui.textBrowser.append(f"<b>Вы:</b> {user_text}")
        response_text, new_mood = send_message_to_chatgpt(user_text, self.bot_mood)
        self.ui.textBrowser.append(f"<b>Курису:</b> {response_text}")

        if new_mood != self.bot_mood:
            self.bot_mood = new_mood
            self.start_animation_for_mood(self.bot_mood)

        self.ui.textEdit.clear()

    def start_animation_for_mood(self, mood):
        folder = os.path.join(EMOTION_PATH, mood)
        if not os.path.isdir(folder):
            print(f"[⚠] Папка для эмоции '{mood}' не найдена: {folder}")
            return

        png_files = sorted(glob.glob(os.path.join(folder, "*.png")))
        if not png_files:
            print(f"[⚠] Нет PNG файлов в папке: {folder}")
            return

        self.current_frames = [QtGui.QPixmap(fn) for fn in png_files]
        self.current_index = 0
        duration = emotion_to_duration_ms.get(mood, 200)
        self.animation_timer.setInterval(duration)
        self.animation_timer.start()

    def update_frame(self):
        if not self.current_frames:
            return
        pixmap = self.current_frames[self.current_index]
        self.ui.label.setPixmap(pixmap)
        self.ui.label.setScaledContents(True)
        self.current_index = (self.current_index + 1) % len(self.current_frames)

# ===== Запуск приложения =====
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ChatWithEmotionApp()
    window.show()
    sys.exit(app.exec())