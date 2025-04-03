import requests

API_KEY = "sk-bf5259625a4d4f05b4c34287b409ac48"

def get_response_deepseek(user_message, chat_history):
    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    chat_history.append({"role": "user", "content": user_message})

    payload = {
        "model": "deepseek-chat",
        "messages": chat_history,
        "temperature": 0.8
    }

    response = requests.post(url, headers=headers, json=payload)

    # Попробуем отловить ошибки
    try:
        result = response.json()

        # Если есть choices — всё норм
        if "choices" in result and result["choices"]:
            reply = result["choices"][0]["message"]["content"]
            chat_history.append({"role": "assistant", "content": reply})
            return reply
        else:
            # Если пришёл не тот формат
            print("\n⚠️ Ответ от API не содержит choices!")
            print("🔎 Вот, что пришло:\n", result)
            return "[Ошибка: неверный формат ответа от API]"
    except Exception as e:
        print("\n❌ Ошибка при обработке ответа:")
        print(response.text)  # покажет сырой текст ответа
        return f"[Ошибка: {e}]"

# Инициализация
chat_history = [
    {"role": "system", "content": "Ты дерзкий и саркастичный помощник. Отвечай дерзко, но не грубо. Иронично помогай."}
]

print("Добро пожаловать в чат с DeepSeek! (напиши 'выход' чтобы выйти)\n")

while True:
    user_input = input("Ты: ")
    if user_input.lower() in ["выход", "exit", "quit"]:
        print("Бот: Ну и проваливай тогда. 🙄")
        break
    reply = get_response_deepseek(user_input, chat_history)
    print("Бот:", reply)

    # sk-bf5259625a4d4f05b4c34287b409ac48