import os
from typing import List
from functools import lru_cache
from langchain_unstructured import UnstructuredLoader
from unstructured.cleaners.core import group_broken_paragraphs, auto_paragraph_grouper
from langchain_core.documents import Document

from text_extractor.text_extractor import Strategy, TextExtractor


class UnstructuredTextExtractor(TextExtractor):
    def __init__(
        self,
        languages: List[str] = [],
        use_cache: bool = True,
        strategy: Strategy = Strategy.AUTO,
    ):
        super().__init__(languages, use_cache, strategy)
        self._loader = None

    @property
    def loader(self) -> UnstructuredLoader:
        if self._loader is None:
            self._loader = UnstructuredLoader(
                partition_via_api=os.getenv("UNSTRUCTURED_API_KEY") is not None,
                strategy=self._strategy.value,
                languages=self._languages,
                post_processors=[group_broken_paragraphs, auto_paragraph_grouper],
            )
        return self._loader

    def _load_file(self, file_path: str) -> list[Document]:
        if self._use_cache:
            cached = self._cache_manager.get(file_path)
            if cached:
                return cached

        self.loader.file_path = file_path
        document = self.loader.load()

        if self._use_cache:
            self._cache_manager.set(file_path, document)

        return document

    @lru_cache
    def get_text_content(self, file_path: str) -> str:
        document = self._load_file(file_path)
        return "\n".join([doc.page_content for doc in document])
