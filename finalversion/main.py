from PyQt6 import QtWidgets
from core.window import BaseLayoutWindow
from core.phone_window import PhoneModeExpanded  # Новый импорт
import sys

class AppController:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.full_window = BaseLayoutWindow()
        self.compact_window = PhoneModeExpanded()  # Новый класс

        # Прокинем ссылку на контроллер, чтобы окна могли переключать друг друга
        self.full_window.controller = self
        self.compact_window.controller = self

    def run(self):
        self.full_window.showFullScreen()
        sys.exit(self.app.exec())

    def switch_to_compact(self):
        self.full_window.hide()
        self.compact_window.show()

    def switch_to_full(self):
        self.compact_window.hide()
        self.full_window.showFullScreen()

if __name__ == "__main__":
    controller = AppController()
    controller.run()