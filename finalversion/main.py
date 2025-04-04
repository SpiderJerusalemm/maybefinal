from PyQt6 import QtWidgets
from core.window import BaseLayoutWindow
from core.phone_window import PhoneModeExpanded  # Новый импорт
import sys
from core.gpt_bridge import init_selenium_connection

class AppController:
    def __init__(self):
        self.driver = None

        # Главное окно
        self.main_window = BaseLayoutWindow()
        self.main_window.controller = self  # 💡 для обратной связи
        self.driver = self.main_window.driver  # использовать уже инициализированный driver

        # Телефонное окно
        self.compact_window = PhoneModeExpanded(driver=self.driver, controller=self)

        self.main_window.show()

        self.always_on_top = True  # или False, если по умолчанию не включено

    def switch_to_compact(self):
        self.main_window.hide()
        self.compact_window.show()

    def switch_to_main(self):
        self.compact_window.hide()
        self.main_window.show()

if __name__ == "__main__":
    import sys
    try:
        app = QtWidgets.QApplication(sys.argv)
        controller = AppController()  # ← где создаётся PhoneModeExpanded
        controller.main_window.show()
        sys.exit(app.exec())
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("❌ Ошибка при запуске — нажмите Enter для выхода.")