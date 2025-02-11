from typing import NamedTuple
from pathlib import Path

class ProcessingError(NamedTuple):
    file: Path
    reason: str
