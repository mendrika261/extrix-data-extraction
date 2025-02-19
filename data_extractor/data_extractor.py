from abc import ABC, abstractmethod
from typing import Any, List
from pydantic import BaseModel, Field

from core.models import DataBaseModel


class DataExtractor(ABC):
    @abstractmethod
    def extract(self, text: str, output_schema: type[DataBaseModel]) -> DataBaseModel:
        """
        Extract structured data from text

        Returns:
            Structured data as a Pydantic model
        """
        pass


class Example(BaseModel):
    role: str = Field(...)
    content: str | Any = Field(...)


class ExamplesJson(BaseModel):
    examples: List[Example] = Field(...)
