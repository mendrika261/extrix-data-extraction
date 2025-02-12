from abc import ABC, abstractmethod
from typing import List, Any

from core.cache_manager import CacheManager

class FileProcessor(ABC):
    def __init__(self, file_path: str, languages: List[str] = None, use_cache: bool = True):
        self._file_path = file_path
        self._languages = languages or ["fr"]
        self._cache_manager = CacheManager()
        self._use_cache = use_cache

    @abstractmethod
    def load_file(self) -> Any:
        """
        Load and process a file
            
        Returns:
            Processed document content
        """
        pass

    @abstractmethod
    def get_text_content(self) -> str:
        """
        Extract text content from a file
            
        Returns:
            Extracted text content
        """
        pass
