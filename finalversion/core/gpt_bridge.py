import re
import time
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
    match = re.search(r"<MOOD\s*=\s*([a-zA-Zа-яА-Я_]+)>", gpt_text)
    return match.group(1).lower() if match else "neutral"


def send_message_to_chatgpt(driver, user_text: str, current_mood: str):
    prompt_text = build_hidden_prompt(user_text, current_mood)

    input_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", input_field)
    input_field.click()
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
    time.sleep(6)

    responses = driver.find_elements(By.CLASS_NAME, "markdown")
    if not responses:
        return "(Бот не ответил)", "neutral"

    raw_response = responses[-1].text
    new_mood = extract_mood_from_response(raw_response)
    cleaned_response = re.sub(r"<MOOD\s*=\s*[a-zA-Zа-яА-Я_]+>", "", raw_response).strip()
    return cleaned_response, new_mood