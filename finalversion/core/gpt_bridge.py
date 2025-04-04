import re
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.constants import EDGE_DEBUG_PORT
from utils.text_prompts import build_hidden_prompt


def init_selenium_connection():
    options = Options()
    options.debugger_address = f"127.0.0.1:{EDGE_DEBUG_PORT}"
    driver = webdriver.Edge(options=options)
    driver.get("https://chat.openai.com")
    print("[OK] Подключились к ChatGPT через Edge")
    return driver


def extract_mood_from_response(gpt_text: str) -> str:
    try:
        match = re.search(r"<MOOD\s*=\s*([a-zA-Zа-яА-Я_]+)>", gpt_text)
        return match.group(1).lower() if match else "neutral"
    except Exception as e:
        print("[GPTBridge] Ошибка при извлечении эмоции:")
        traceback.print_exc()
        return "neutral"


def send_message_to_chatgpt(driver, user_text: str, current_mood: str):
    prompt_text = build_hidden_prompt(user_text, current_mood)

    try:
        input_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
        )

        # Принудительный фокус
        driver.execute_script("arguments[0].scrollIntoView(true);", input_field)
        driver.execute_script("arguments[0].focus();", input_field)
        input_field.click()
        time.sleep(0.2)

        # Очистка и ввод
        input_field.send_keys(Keys.CONTROL + "a", Keys.DELETE)

        driver.execute_script("""
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
        """, input_field, prompt_text)

        input_field.send_keys(Keys.ENTER)
        time.sleep(6)  # Ожидаем, пока GPT ответит

        # Извлечение ответа
        responses = driver.find_elements(By.CLASS_NAME, "markdown")
        if not responses:
            print("[GPTBridge] Не найден ответ от GPT")
            return "(Бот не ответил)", "neutral"

        raw_response = responses[-1].text
        print("[GPTBridge] Ответ от GPT:\n", raw_response)

        new_mood = extract_mood_from_response(raw_response)
        cleaned_response = re.sub(r"<MOOD\s*=\s*[a-zA-Zа-яА-Я_]+>", "", raw_response).strip()

        print("[GPTBridge] Очищенный ответ:", cleaned_response)
        print("[GPTBridge] Эмоция:", new_mood)

        return cleaned_response, new_mood

    except Exception as e:
        print("[GPTBridge] Ошибка при отправке или обработке ответа:")
        traceback.print_exc()
        return "(Ошибка при отправке сообщения)", "neutral"
