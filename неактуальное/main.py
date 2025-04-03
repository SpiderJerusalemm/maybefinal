import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog
from deepPavlov import DialogBotV1, H2PersonaChatHyperparametersV1
from labdab1 import Ui_MainWindow   # Интерфейс окна авторизации
from new_window import Ui_Dialog      # Интерфейс дочернего окна (например, "Dashboard")
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

PRETRAINED_MODEL_NAME_OR_PATH = "C:\\Users\\user\\Music\\saved_model1"
PAIR_DIALOG_HISTORY_LENGTH = 4
CHAT_MAX_LENGTH = 25
PERSONA_MAX_LENGTH = 50

# Загружаем токенизатор
tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_MODEL_NAME_OR_PATH)
# Загружаем модель и увеличиваем размер эмбеддингов, чтобы учесть новые токены
model = AutoModelForSeq2SeqLM.from_pretrained(PRETRAINED_MODEL_NAME_OR_PATH)
# Перенос модели на нужное устройство
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device).eval()
if torch.cuda.is_available():
    model.half()

# Настройка гиперпараметров
hyperparameters = H2PersonaChatHyperparametersV1(
    chat_history_pair_length=PAIR_DIALOG_HISTORY_LENGTH,
    persona_max_length=PERSONA_MAX_LENGTH,
    chat_max_length=CHAT_MAX_LENGTH,
    model_name=PRETRAINED_MODEL_NAME_OR_PATH,
)

# Изначальные данные персоны и история
persona = []
history = []

chatbot = DialogBotV1(
    model=model,
    tokenizer=tokenizer,
    hyperparameters=hyperparameters,
    history=history,
    persona=persona,
    device=device,
)

class DashboardWindow(QDialog):
    def __init__(self, chatbot, parent=None):
        super(DashboardWindow, self).__init__(parent)
        self.chatbot = chatbot
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.messageButton.setAutoDefault(False)
        self.ui.messageButton.setDefault(False)
        self.ui.messageButton.setShortcut("")
        self.chat()
        
    def chat(self):
        self.ui.messageButton.clicked.connect(self.send_message)

    def send_message(self):
        try:
            user_message = self.ui.MyText.toPlainText()
            if user_message:
                self.ui.MyText.clear()
                # self.ui.ChatHystory.append("Вы: " + user_message)
                self.ui.ChatHystory.append("Вы: " + user_message)
                # Добавляем сообщение пользователя в историю диалога чат-бота
                # self.chatbot.history.append("Вы: " + user_message)
                self.chatbot.history.append(user_message)
                response = self.chatbot.next_response(max_new_tokens=60, penalty_alpha=0.35, top_k=15)
                self.ui.ChatHystory.append("Бот: " + response)
                print("Сообщение отправлено, получен ответ.")
        except Exception as e:
            print("Ошибка при отправке сообщения:", e)

class ExpenseTracer(QMainWindow):
    def __init__(self, chatbot):
        super(ExpenseTracer, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.chatbot = chatbot
        self.correct_login = "admin"
        self.correct_password = "12345"
        # Подключаем кнопку авторизации к методу проверки
        self.ui.loginButton.clicked.connect(self.handle_login)
        # Сохраняем ссылку на дочернее окно, чтобы оно не закрывалось сборщиком мусора
        self.dashboard = None

    def handle_login(self):
        # Получаем введенные данные из полей
        login = self.ui.loginLineEdit.text()
        password = self.ui.passwordlineEdit.text()

        # Сравниваем с заданными данными
        if login == self.correct_login and password == self.correct_password:
            QMessageBox.information(self, "Авторизация", "welcome!")
            self.open_dashboard()
        else:
            QMessageBox.warning(self, "Авторизация", "Неверный логин или пароль!")

    def open_dashboard(self):
        # Создаем и открываем новое окно (дочернее окно)
        self.dashboard = DashboardWindow(self.chatbot, self)
        self.dashboard.show()
        # Можно скрыть окно авторизации, если оно больше не нужно
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseTracer(chatbot)
    window.show()
    sys.exit(app.exec())