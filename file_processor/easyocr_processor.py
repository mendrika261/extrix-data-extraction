from typing import List, Any
from functools import lru_cache
import easyocr

from file_processor.interface import FileProcessor
from core.utils import handle_document_images_or_texts


class EasyOCRProcessor(FileProcessor):
    def __init__(self, file_path: str, languages: List[str] = None, use_cache: bool = True):
        super().__init__(file_path, languages or ['fr'])
        self._use_cache = use_cache
        self._reader = None

    @property
    def reader(self):
        if self._reader is None:
            self._reader = easyocr.Reader(
                lang_list=self._languages,
                gpu=True
            )
        return self._reader

    def process_image(self, image_path: str) -> List[tuple]:
        return self.reader.readtext(image_path)

    def load_file(self) -> Any:
        if self._use_cache:
            cached = self._cache_manager.get(self._file_path)
            if cached:
                return cached

        results = handle_document_images_or_texts(self._file_path, self.process_image)
        flattened_results = [item for sublist in results for item in sublist]
        
        if self._use_cache:
            self._cache_manager.set(self._file_path, flattened_results)
            
        return flattened_results

    @lru_cache
    def get_text_content(self) -> str:
        ocr_results = self.load_file()
        return '\n'.join(text for _, text, _ in ocr_results)
