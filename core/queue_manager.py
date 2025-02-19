from datetime import datetime, timedelta
from threading import Lock


class QueueManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, max_items: int, time_limit: int):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize(max_items, time_limit)
        return cls._instance

    def _initialize(self, max_items: int, time_limit: int):
        print("Limiting to", max_items, "items in", time_limit, "minutes")
        self.max_items = max_items
        self.time_limit = time_limit
        self.processing_time = datetime.now()
        self.items_processed = 0

    def can_process(self) -> bool:
        if self._should_reset():
            self._reset()
        return self.items_processed < self.max_items

    def increment_processed(self) -> None:
        with self._lock:
            self.items_processed += 1

    def _should_reset(self) -> bool:
        time_elapsed = datetime.now() - self.processing_time
        return time_elapsed >= timedelta(minutes=self.time_limit)

    def _reset(self) -> None:
        self.processing_time = datetime.now()
        self.items_processed = 0
