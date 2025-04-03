import json
from torch.utils.data import Dataset
import torch

class ContextResponseDataset(Dataset):
    def __init__(self, data_path, tokenizer, max_context_length=128, max_response_length=64):
        """
        Args:
            data_path (str): Путь к JSON-файлу с данными.
            tokenizer: Токенизатор из библиотеки transformers.
            max_context_length (int): Максимальная длина токенизированного контекста.
            max_response_length (int): Максимальная длина токенизированного ответа.
        """
        with open("C:\\Users\\user\\Music\\dataset1.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer
        self.max_context_length = max_context_length
        self.max_response_length = max_response_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]
        context = sample["context"]
        response = sample["response"]
        
        # Токенизация контекста
        context_enc = self.tokenizer.encode_plus(
            context,
            add_special_tokens=True,
            truncation=True,
            max_length=self.max_context_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        # Токенизация ответа (target)
        response_enc = self.tokenizer.encode_plus(
            response,
            add_special_tokens=True,
            truncation=True,
            max_length=self.max_response_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        # Получаем labels из токенизированного ответа
        labels = response_enc["input_ids"].squeeze()
        # Заменяем токены паддинга на -100, чтобы они не учитывались в loss
        labels[labels == self.tokenizer.pad_token_id] = -100
        
        return {
            "input_ids": context_enc["input_ids"].squeeze(),        # Токенизированный контекст
            "attention_mask": context_enc["attention_mask"].squeeze(),  # Маска внимания для контекста
            "labels": labels                                          # Токенизированный ответ
        }

# Пример использования:
if __name__ == "__main__":
    from transformers import AutoTokenizer

    # Замените на имя вашей предобученной модели, например, "facebook/bart-base"
    model_name = "DeepPavlov/mbart-large-50-ru-persona-chat"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Путь к файлу dataset.json, где данные должны быть в формате:
    # [
    #    {
    #      "context": "Пользователь: Привет, напомни, пожалуйста, купить хлеб вечером.\nАссистент:",
    #      "response": "Конечно, вечером напомню тебе про хлеб."
    #    },
    #    ...
    # ]
    data_path = "C:\\Users\\user\\Music\\dataset1.json"
    
    dataset = ContextResponseDataset(data_path, tokenizer, max_context_length=128, max_response_length=64)
    
    print("Размер датасета:", len(dataset))
    sample = dataset[0]
    print("Пример входных данных:")
    print("input_ids:", sample["input_ids"])
    print("attention_mask:", sample["attention_mask"])
    print("labels:", sample["labels"])