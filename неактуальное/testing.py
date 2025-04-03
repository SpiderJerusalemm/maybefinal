import sys
import os
import glob

from PyQt6 import QtWidgets, QtGui, QtCore
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

from test1 import Ui_Dialog  # Ваш сгенерированный файлик из Qt Designer

# ====== ИНИЦИАЛИЗАЦИЯ МОДЕЛИ / ТОКЕНИЗАТОРА ======
model_name = "Djacon/rubert-tiny2-russian-emotion-detection"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

def analyze_emotion(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    probs = torch.nn.functional.softmax(logits, dim=1)
    predicted_class = torch.argmax(probs, dim=1).item()
    label = model.config.id2label.get(predicted_class, str(predicted_class))
    return label, probs

# Сопоставляем эмоцию с папкой, где лежат PNG-кадры
emotion_to_folder = {
    # "happy":   r"C:\Users\user\Music\project\amadeus_emotion\happy_frames",
    "anger":   r"C:\Users\user\Music\project\amadeus_emotion\anger",
    "neutral": r"C:\Users\user\Music\project\amadeus_emotion\neutral",
    "joy":     r"C:\Users\user\Music\project\amadeus_emotion\joy"
    # дополняйте при необходимости
}

# «Скрытые» ответы для каждой эмоции (пример)
emotion_to_hidden_response = {
    "happy":   "Я рад за тебя!",
    "anger":   "дурак",
    "neutral": "Ну ладно...",
    "joy":     "Ух ты, здорово!"
}

# При желании, можно сделать разную скорость прокрутки для разных эмоций
emotion_to_duration_ms = {
    "happy":   150,
    "anger":   150,
    "neutral": 150,
    "joy":     150
}


class EmotionApp(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Подключаем кнопку
        self.ui.pushButton.clicked.connect(self.process_text)

        # QTimer для прокрутки кадров
        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.timeout.connect(self.update_frame)

        # Здесь храним текущие кадры и индекс
        self.current_frames = []
        self.current_index = 0

        # Можно хранить «последний ответ», если он нужен
        self.hidden_emotion_response = ""

    def process_text(self):
        """
        Срабатывает при клике на кнопку.
        1) Определяем эмоцию
        2) Грузим соответствующие PNG-кадры
        3) Запускаем анимацию
        """
        text = self.ui.textEdit.toPlainText()
        if not text.strip():
            return

        # 1) Определяем эмоцию
        emotion, probs = analyze_emotion(text)
        print(f"Определённая эмоция: {emotion}")
        print(f"Вероятности: {probs}")

        # 2) Запоминаем «скрытый» ответ для этой эмоции
        self.hidden_emotion_response = emotion_to_hidden_response.get(emotion, "")
        print("Скрытый ответ:", self.hidden_emotion_response)
        # По умолчанию этот ответ в GUI не выводится, но вы можете
        # где-то его сохранить, отправить в лог или что угодно.

        # 3) Грузим соответствующие кадры
        folder = emotion_to_folder.get(emotion, "")
        if not folder or not os.path.isdir(folder):
            # Если вдруг нет папки для этой эмоции, выходим
            print(f"Нет папки для эмоции {emotion} или она не существует: {folder}")
            return

        # Загружаем все PNG-кадры, сортируем по имени файла
        png_files = sorted(glob.glob(os.path.join(folder, "*.png")))
        if not png_files:
            print(f"Не найдено PNG-файлов в папке {folder}")
            return

        # Создаём список QPixmap
        self.current_frames = [QtGui.QPixmap(fn) for fn in png_files]
        self.current_index = 0

        # (Не обязательно) Меняем интервал таймера под конкретную эмоцию
        duration = emotion_to_duration_ms.get(emotion, 300)
        self.animation_timer.setInterval(duration)

        # Запускаем анимацию (если таймер уже работал, сбросим)
        self.animation_timer.start()

    def update_frame(self):
        """
        Функция, которую вызывает QTimer по истечению интервала.
        Меняем кадр на следующий.
        """
        if not self.current_frames:
            return

        # Устанавливаем кадр на label
        pixmap = self.current_frames[self.current_index]
        self.ui.label.setPixmap(pixmap)
        self.ui.label.setScaledContents(True)

        # Переходим к следующему
        self.current_index = (self.current_index + 1) % len(self.current_frames)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = EmotionApp()
    window.show()
    sys.exit(app.exec())