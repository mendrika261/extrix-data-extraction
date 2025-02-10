from diskcache import Cache
import os
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()
CACHE_DIR: str = os.getenv("CACHE_DIR", "./tmp/cache")

class CacheManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            load_dotenv()
            cls._instance.cache_dir = CACHE_DIR
            cls._instance.cache = Cache(cls._instance.cache_dir)
        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self.cache.set(key, value)
