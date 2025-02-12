import warnings
from typing import List, Any
from functools import lru_cache
from PIL import Image

from file_processor.file_processor import FileProcessor
from core.utils import handle_document_images_or_texts, is_macos
from core.exceptions import OSNotSupportedError, OSCompatibilityWarning


class TesserOCRProcessor(FileProcessor):
    def __init__(self, file_path: str, languages: List[str] = None, use_cache: bool = True):
        if is_macos():
            raise OSNotSupportedError("TesserOCR library", "macOS")

        warnings.warn(
            "TesserOCR library compatibility is not fully tested",
            OSCompatibilityWarning
        )
        
        super().__init__(file_path, languages or ['fra'])
        self._use_cache = use_cache
        self._api = None

    @property
    def api(self):
        import tesserocr
        if self._api is None:
            self._api = tesserocr.PyTessBaseAPI(lang='+'.join(self._languages))
        return self._api

    def process_image(self, image_path: str) -> str:
        with Image.open(image_path) as img:
            self.api.SetImage(img)
            return self.api.GetUTF8Text()

    def load_file(self) -> Any:
        if self._use_cache:
            cached = self._cache_manager.get(self._file_path)
            if cached:
                return cached

        results = handle_document_images_or_texts(self._file_path, self.process_image)
        
        if self._use_cache:
            self._cache_manager.set(self._file_path, results)
            
        return results

    @lru_cache
    def get_text_content(self) -> str:
        results = self.load_file()
        return '\n'.join(results)

    def __del__(self):
        if self._api:
            self._api.End()
