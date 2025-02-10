from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel

class DataExtractor(ABC):
    @abstractmethod
    def extract(self) -> BaseModel:
        """
        Extract structured data from text
            
        Returns:
            Structured data as a Pydantic model
        """
        pass
