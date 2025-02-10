from functools import lru_cache
from typing import Any, List, Type
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import init_chat_model

from core.utils import load_json_file
from core.monitoring import MonitoringCallbackHandler
from data_extractor.interface import DataExtractor

class Example(BaseModel):
    role: str = Field(...)
    content: str|Any = Field(...)

class ExamplesJson(BaseModel):
    examples: List[Example] = Field(...)

class LLMDataExtractor(DataExtractor):
    def __init__(self,
                 model_name: str = "gemini-1.5-pro",
                 provider: str = "google-genai",
                 temperature: float = 0.1):
        super().__init__()
        
        self.monitoring_handler = MonitoringCallbackHandler(model_name, provider)
        
        self._llm = init_chat_model(
            model=model_name,
            model_provider=provider,
            temperature=temperature,
            callbacks=[self.monitoring_handler]
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

    def start_monitoring(self, text: str) -> None:
        self.monitoring_handler.input_tokens = len(text.split())
        

    def extract(self,
                text: str,
                output_schema: Type[BaseModel]) -> BaseModel:
        self.start_monitoring(text)
        
        prompt = self._prompt_template.invoke({
            "text": text,
            "examples": self._examples
        })
        result = self._get_structured_llm(output_schema).invoke(prompt)
        
        return result

    def load_examples_json(self, examples: List[Example]) -> None:
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
