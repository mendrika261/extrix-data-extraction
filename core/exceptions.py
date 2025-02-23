from pathlib import Path
from typing import NamedTuple

from pydantic import ValidationError as PydanticValidationError


class ExtrixException(Exception):
    pass


class OSNotSupportedError(ExtrixException):
    def __init__(self, processor_name: str, platform: str):
        self.processor_name = processor_name
        self.platform = platform
        super().__init__(f"{processor_name} is not supported on {platform}")


class ValidationError(NamedTuple):
    file: Path
    reason: str
