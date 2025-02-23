from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Type
from pydantic import BaseModel, ValidationError
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import PydanticOutputParser

from cli.ui import CONSOLE
from core.models import DataBaseModel
from core.utils import load_json_file
from core.monitoring import MonitoringCallbackHandler
from data_extractor.data_extractor import DataExtractor, Example, ExamplesJson


class LLMDataExtractor(DataExtractor):
    def __init__(
        self,
        llm_model: str,
        llm_provider: str,
        llm_temperature: float = 0.1,
        examples: List[Example] | None = None,
        examples_path: Path | None = None,
        **kwargs,
    ):
        super().__init__()
        self._examples = []
        self.monitoring_handler = MonitoringCallbackHandler(llm_model, llm_provider)

        self._llm = init_chat_model(
            model=llm_model,
            model_provider=llm_provider,
            temperature=llm_temperature,
            callbacks=[self.monitoring_handler],
        )

        if examples:
            self.load_examples_json(examples)
        elif examples_path:
            self.load_examples_json_file(examples_path)

    def _extract_without_tooling(
        self, text: str, output_schema: Type[DataBaseModel]
    ) -> DataBaseModel:
        parser = PydanticOutputParser(pydantic_object=output_schema)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert extraction algorithm. Strictly respect output required and types."
                    "Wrap the output in `json` tags\n{format_instructions}",
                ),
                MessagesPlaceholder("examples"),
                ("human", "{text}"),
            ]
        ).partial(
            format_instructions=parser.get_format_instructions(),
            examples=self._examples,
        )
        chain = prompt | self._llm | parser
        return chain.invoke({"text": text})

    def _extract_with_tooling(
        self, text: str, output_schema: Type[DataBaseModel]
    ) -> DataBaseModel:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert extraction algorithm. Strictly respect output required and types.",
                ),
                MessagesPlaceholder("examples"),
                ("human", "{text}"),
            ]
        )
        prompt = prompt_template.invoke({"text": text, "examples": self._examples})
        llm = self._llm.with_structured_output(schema=output_schema)
        result = llm.invoke(prompt)
        return output_schema.model_validate(result)

    def extract(self, text: str, output_schema: Type[DataBaseModel]) -> DataBaseModel:
        self.start_monitoring(text)

        result = None
        try:
            result = self._extract_with_tooling(text, output_schema)
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            CONSOLE.print(
                "Structured output not supported by the model. "
                "Trying without tooling. It may fail."
            )
            result = self._extract_without_tooling(text, output_schema)

        self.stop_monitoring(result)
        return result

    def load_examples_json(self, examples: Dict[str, Any]) -> None:
        self._examples = [
            {"role": example["role"], "content": str(example["content"])}  # type: ignore
            for example in examples
        ]

    @lru_cache
    def load_examples_json_file(self, json_file_path: Path) -> None:
        json = load_json_file(json_file_path)
        ExamplesJson.model_validate(json)
        self.load_examples_json(json["examples"])

    def start_monitoring(self, text: str) -> None:
        self.monitoring_handler.input_tokens = len(text.split())

    def stop_monitoring(self, result: BaseModel) -> None:
        self.monitoring_handler.output_tokens = len(str(result).split())
