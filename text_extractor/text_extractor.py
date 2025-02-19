from abc import ABC, abstractmethod
from enum import Enum
from functools import lru_cache
from typing import List

from core.cache_manager import CacheManager


class Strategy(Enum):
    AUTO = "auto"
    HI_RES = "hi_res"
    FAST = "fast"


class TextExtractor(ABC):
    def __init__(
        self,
        languages: List[str] | None = None,
        use_cache: bool = True,
        strategy: Strategy = Strategy.AUTO,
    ):
        self._languages = languages or []
        self._use_cache = use_cache
        self._cache_manager = CacheManager()
        self._strategy = strategy

    @abstractmethod
    @lru_cache
    def get_text_content(self, file_path: str) -> str:
        """
        Extract text content from a file

        Returns:
            Extracted text content
        """
        pass
