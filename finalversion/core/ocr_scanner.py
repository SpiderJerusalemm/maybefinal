from PIL import Image
import pyautogui
import pytesseract

def capture_screen_text(crop_box=None) -> str:
    try:
        screenshot = pyautogui.screenshot()
        image = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())

        if crop_box:
            image = image.crop(crop_box)

        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        text = pytesseract.image_to_string(image, lang='eng+rus')
        return text.strip()

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ""