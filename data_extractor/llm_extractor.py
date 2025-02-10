from functools import lru_cache
from typing import Any, Dict, List, Type
from matplotlib.pyplot import cla
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import init_chat_model
from regex import E, P

from core.utils import load_json_file
from data_extractor.interface import DataExtractor

class Example(BaseModel):
    role: str = Field(...)
    content: str = Field(...)

class ExamplesJson(BaseModel):
    examples: List[Example] = Field(...)

class LLMDataExtractor(DataExtractor):
    def __init__(self,
                 model_name: str = "gemini-1.5-pro",
                 provider: str = "google-genai",
                 temperature: float = 0.5):
        super().__init__()
        self._examples = []

        self._llm = init_chat_model(
            model=model_name,
            model_provider=provider,
            temperature=temperature,
        )
        self._prompt_template = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert extraction algorithm. "
                "Extract information from the text strictly following example schema."
            ),
            MessagesPlaceholder('examples'),
            ("human", "{text}"),
        ])
        

    def _get_structured_llm(self, output_schema: Type[BaseModel]) -> BaseCallbackHandler:
        return self._llm.with_structured_output(schema=output_schema)

    def extract(self,
                text: str,
                output_schema: Type[BaseModel]) -> BaseModel:
        prompt = self._prompt_template.invoke({
            "text": text,
            "examples": self._examples
        })
        return self._get_structured_llm(output_schema).invoke(prompt)

    def load_examples_json(self, examples: List[Dict[str, Any]]) -> None:
        self._examples = [
            {
                "role": example["role"],
                "content": str(example["content"])
            }
            for example in examples
        ]

    @lru_cache
    def load_examples_json_file(self, json_file_path: str) -> None:
        json = load_json_file(json_file_path)
        ExamplesJson.model_validate(json)
        self.load_examples_json(json['examples'])
        