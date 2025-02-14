from functools import lru_cache
from typing import List, Type
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import PydanticOutputParser

from cli.ui import CONSOLE
from core.utils import load_json_file
from core.monitoring import MonitoringCallbackHandler
from data_extractor.data_extractor import DataExtractor, Example, ExamplesJson

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

    def _extract_without_tooling(self,
                text: str,
                output_schema: Type[BaseModel]) -> BaseModel:
        parser = PydanticOutputParser(pydantic_object=output_schema)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert extraction algorithm."
             "Wrap the output in `json` tags\n{format_instructions}"),
            MessagesPlaceholder('examples'),
            ("human", "{text}"),
        ]).partial(
            format_instructions=parser.get_format_instructions(),
            examples=self._examples,
        )
        chain = prompt | self._llm | parser
        return chain.invoke(text)

    def _get_structured_llm(self, output_schema: Type[BaseModel]) -> BaseCallbackHandler:
        return self._llm.with_structured_output(schema=output_schema)

    def _extract_with_tooling(self,
                text: str,
                output_schema: Type[BaseModel]) -> BaseModel:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert extraction algorithm."),
            MessagesPlaceholder('examples'),
            ("human", "{text}"),
        ])
        prompt = prompt_template.invoke({"text": text, "examples": self._examples})
        llm = self._llm.with_structured_output(schema=output_schema)
        return llm.invoke(prompt)

    def extract(self,
                text: str,
                output_schema: Type[BaseModel]) -> BaseModel:
        self.start_monitoring(text)

        result = None
        try:
            result = self._extract_with_tooling(text, output_schema)
        except Exception:
            CONSOLE.print("Structured output not supported by the model. "
                            "Trying without tooling. It may fail.")
            result = self._extract_without_tooling(text, output_schema)
                

        self.stop_monitoring(result)
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

    def start_monitoring(self, text: str) -> None:
        self.monitoring_handler.input_tokens = len(text.split())

    def stop_monitoring(self, result: BaseModel) -> None:
        self.monitoring_handler.output_tokens = len(str(result).split())        
