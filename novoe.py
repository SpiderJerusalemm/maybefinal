from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

options = Options()
options.debugger_address = "127.0.0.1:9222"  # подключение к уже открытому браузеру

driver = webdriver.Edge(options=options)

# Теперь браузер уже открыт, и мы не ловим капчу 🎉
print("[✓] Подключились к существующей сессии Edge.")
driver.get("https://chat.openai.com")

while True:
    user_input = input("Ты: ")
    if user_input.lower() in ["выход", "exit", "quit"]:
        print("Бот: Всё, ухожу 👋")
        break

    try:
        input_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
        )
        input_field.click()
        input_field.send_keys(user_input)
        input_field.send_keys(Keys.ENTER)

        print("⏳ GPT думает...")
        time.sleep(10)

        responses = driver.find_elements(By.CLASS_NAME, "markdown")
        if responses:
            print("Бот:", responses[-1].text)
        else:
            print("Бот не ответил 🤷‍♂️")

    except Exception as e:
        import traceback
        print("⚠️ Произошла ошибка:")
        traceback.print_exc()