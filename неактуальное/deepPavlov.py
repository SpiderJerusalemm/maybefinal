from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from dataclasses import dataclass
from typing import List, TypedDict
from itertools import chain

@dataclass
class H2PersonaChatHyperparametersV1:
    """
    chat_history_pair_length: int - количество пар диалога с конца
    """
    model_name: str = "facebook/bart-base"
    chat_history_pair_length: int = 7
    persona_max_length: int = 14
    chat_max_length: int = 25
    debug_status: int = 0

class PersonaChatDatasetSampleV1(TypedDict):
    """
    persona: List[str] - набор предложений фактов персоны
    history: List[str] - набор предложений истории переписки
    """
    persona: List[str]
    history: List[str]
    sample_id: str

class H2Seq2SeqInferenceSampleDictV1(TypedDict):
    input_ids: List[int]
    attention_mask: List[int]

def flat_list(list_of_lists: List[List]) -> List:
    return list(chain.from_iterable(list_of_lists))

class H2Seq2SeqInferencePersonaSampleV1:
    def __init__(
        self,
        dataset_sample: PersonaChatDatasetSampleV1,
        tokenizer: AutoTokenizer,
        hyperparameters: H2PersonaChatHyperparametersV1,
    ) -> None:
        self.dataset_sample = dataset_sample
        self.tokenizer = tokenizer
        self.hyperparameters = hyperparameters

    def add_spaces_after(self, items: List[str]) -> List[str]:
        return [item + " " for item in items]

    @property
    def bos_token_id(self):
        if "t5" in self.hyperparameters.model_name:
            return []
        if self.tokenizer.bos_token_id is None:
            return []
        return [self.tokenizer.bos_token_id]

    @property
    def eos_token_id(self):
        if self.tokenizer.eos_token_id is None:
            return []
        return [self.tokenizer.eos_token_id]

    def add_sep_beetween(self, items: List[str], sep=" ") -> List[str]:
        for i in range(1, len(items)):
            items[i] = sep + items[i]
        return items

    def add_spaces_between(self, items: List[str]) -> List[str]:
        if not items:
            return items
        items = self.add_spaces_after(items)
        items[-1] = items[-1].strip()
        return items

    def get_sample(self) -> H2Seq2SeqInferenceSampleDictV1:
    # Получаем историю диалога и, если она пустая, подставляем пустую строку
        dialog_history = self.dataset_sample["history"]
        if not dialog_history:
            dialog_history = [""]
        dialog_history = dialog_history[-self.hyperparameters.chat_history_pair_length * 2 - 1 :]
        dialog_history = self.add_sep_beetween(dialog_history)

        # Получаем набор фактов персоны и, если он пустой, подставляем пустую строку
        persona = self.dataset_sample["persona"]
        if not persona:
            persona = [""]
        persona = self.add_sep_beetween(persona, sep=" ")

        encoded_history = self.tokenizer.batch_encode_plus(
            dialog_history,
            add_special_tokens=False,
            truncation=True,
            max_length=self.hyperparameters.chat_max_length,
        )
        encoded_history = flat_list(encoded_history["input_ids"])

        encoded_persona = self.tokenizer.batch_encode_plus(
            persona,
            add_special_tokens=False,
            truncation=True,
            max_length=self.hyperparameters.persona_max_length,
        )
        encoded_persona = flat_list(encoded_persona["input_ids"])

        input_ids = [
            *self.bos_token_id,
            *encoded_persona,   # если вам надо оставить "persona"  
            *encoded_history,   # добавляете просто диалоговую историю
            *self.eos_token_id,
        ]
        # Если input_ids по каким-то причинам получился пустым, подставляем хотя бы eos-токен
        if not input_ids and self.tokenizer.eos_token_id is not None:
            input_ids = [self.tokenizer.eos_token_id]

        attention_mask = [1] * len(input_ids)
        return H2Seq2SeqInferenceSampleDictV1(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )

class DialogBotV1:
    def __init__(
        self,
        model: AutoModelForSeq2SeqLM,
        tokenizer: AutoTokenizer,
        hyperparameters: H2PersonaChatHyperparametersV1,
        history: List[str] = None,
        persona: List[str] = None,
        device: str = "cuda",
        shuffle_persona: bool = True,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.hyperparameters = hyperparameters
        self.device = device
        self.shuffle_persona = shuffle_persona
        self.debug_status = hyperparameters.debug_status
        self.history = history if history is not None else []
        self.persona = persona if persona is not None else []

    def _get_sample(
        self,
        persona: List[str],
        history: List[str],
    ) -> H2Seq2SeqInferenceSampleDictV1:
        dataset_sample = PersonaChatDatasetSampleV1(
            persona=persona,
            history=history,
            sample_id=""
        )
        sample = H2Seq2SeqInferencePersonaSampleV1(
            tokenizer=self.tokenizer,
            hyperparameters=self.hyperparameters,
            dataset_sample=dataset_sample,
        )
        sample = sample.get_sample()
        for key in sample.keys():
            sample[key] = torch.tensor(sample[key]).unsqueeze(0).to(self.device)
        return sample

    def next_response(self, **generation_params) -> str:
        sample = self._get_sample(persona=self.persona, history=self.history)
        decoded_prompt = self.tokenizer.decode(sample["input_ids"][0])
        print("Декодированный prompt:", decoded_prompt)
        generated = self.generate_response(sample, **generation_params)
        decoded = self.tokenizer.batch_decode(generated, skip_special_tokens=True)
        print("Сгенерированные токены:", generated)
        print("Декодированный результат:", decoded)
        if decoded and len(decoded) > 0:
            answer = decoded[0]
            self.history.append(answer)
            return answer
        else:
            error_message = "Не удалось сгенерировать ответ."
            self.history.append(error_message)
            return error_message

    def generate_response(
        self,
        sample: H2Seq2SeqInferenceSampleDictV1,
        **generation_params,
    ):
        with torch.no_grad():
            return self.model.generate(
                **sample,
                decoder_start_token_id=self.tokenizer.lang_code_to_id["ru_RU"],
                **generation_params,
        )