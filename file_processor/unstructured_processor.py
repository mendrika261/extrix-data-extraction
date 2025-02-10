from typing import List, Any
from functools import lru_cache
from dotenv import load_dotenv
from langchain_unstructured import UnstructuredLoader
from unstructured.cleaners.core import (
    group_broken_paragraphs,
    auto_paragraph_grouper
)

from file_processor.interface import FileProcessor


class UnstructuredFileProcessor(FileProcessor):
    def __init__(self, file_path, languages: List[str] = None, strategy: str = None, use_cache: bool = True):
        super().__init__(file_path, languages)
        self._strategy = strategy
        self._use_cache = use_cache

    def load_file(self) -> Any:
        if self._use_cache:
            cached = self._cache_manager.get(self._file_path)
            if cached:
                return cached

        loader = UnstructuredLoader(
            file_path=self._file_path,
            strategy=self._strategy,
            languages=self._languages,
            post_processors=[group_broken_paragraphs, auto_paragraph_grouper],
        )
        document = loader.load()
        
        if self._use_cache:
            self._cache_manager.set(self._file_path, document)
            
        return document

    @lru_cache
    def get_text_content(self) -> str:
        document = self.load_file()
        return "\n".join([doc.page_content for doc in document])
