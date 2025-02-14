from abc import ABC, abstractmethod
from typing import Any, List
from pydantic import BaseModel, Field

class DataExtractor(ABC):
    @abstractmethod
    def extract(self) -> BaseModel:
        """
        Extract structured data from text
            
        Returns:
            Structured data as a Pydantic model
        """
        pass

class Example(BaseModel):
    role: str = Field(...)
    content: str|Any = Field(...)

class ExamplesJson(BaseModel):
    examples: List[Example] = Field(...)