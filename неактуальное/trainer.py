import torch
from transformers import Trainer, TrainingArguments
from custom import ContextResponseDataset
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


# Задаём имя модели (имя нейросети) — это название модели из HuggingFace
model_name = "C:/Users/user/Music/saved_model1"
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Путь к датасету. Файл dataset.json должен содержать данные в формате:
# [
#   {
#     "context": "Пользователь: Привет, напомни, пожалуйста, купить хлеб вечером.\nАссистент:",
#     "response": "Конечно, вечером напомню тебе про хлеб."
#   },
#   ...
# ]
data_path = "C:\\Users\\user\\Music\\dataset1.json"

# Параметры для токенизации
max_context_length = 128
max_response_length = 64

# Инициализируем датасет
train_dataset = ContextResponseDataset(data_path, tokenizer, max_context_length, max_response_length)

# Настройки обучения
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=5e-5,
    weight_decay=0.01,
    
    evaluation_strategy="no",   # <-- Отключаем оценку
    logging_strategy="steps",   # или "no" — смотрите, как удобнее
    save_strategy="epoch",      # при желании можно продолжать сохранять чекпоинты раз в эпоху
    
    load_best_model_at_end=False,  # если нет eval, то 'лучшую' модель не отследить
    fp16=torch.cuda.is_available()
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    # нет eval_dataset
)
trainer.train()

# Запуск дообучения
trainer.train()

# Сохраняем дообученную модель и токенизатор
model.save_pretrained("C:\\Users\\user\\Music\\saved_model1")
tokenizer.save_pretrained("C:\\Users\\user\\Music\\saved_model1")