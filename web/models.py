from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime, timezone
from text_extractor.unstructured import Strategy

from core.models import DataBaseModel
from core.model_factory import ModelFactory


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    fetched: bool = False


class ExtractorConfig(BaseModel):
    languages: list[str] = ["fr"]
    strategy: Strategy = Strategy.AUTO
    no_cache: bool = True
    text_extractor: str = "unstructured"
    data_extractor: str = "llm"
    llm_model: str = "gemini-1.5-pro"
    llm_provider: str = "google-genai"
    llm_temperature: float = 0.1
    examples: Optional[list[dict]] = None
    output_schema: Dict[str, Any]


class ExtractionRequest(BaseModel):
    config: ExtractorConfig
