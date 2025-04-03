# core/fonts.py
from PyQt6.QtGui import QFontDatabase, QFont
import os

def load_custom_fonts():
    fonts_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
    font_path = os.path.join(fonts_dir, "EBGaramond-Bold.ttf")

    font_id = QFontDatabase.addApplicationFont(font_path)
    family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Courier New"
    return family