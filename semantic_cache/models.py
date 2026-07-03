from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class ResponseSource(str, Enum):
    EXACT_CACHE = "EXACT_CACHE"
    SEMANTIC_CACHE = "SEMANTIC_CACHE"
    LLM = "LLM"

class CacheRecord(BaseModel):
    id: Optional[int] = None
    faiss_id: Optional[int] = None
    prompt: str
    fingerprint: str
    response: str
    provider: str
    model: str
    temperature: float
    timestamp: datetime = Field(default_factory=datetime.now)
    ttl: int = 0
    hit_count: int = 0
    last_accessed: datetime = Field(default_factory=datetime.now)

class RequestRecord(BaseModel):
    id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    prompt: str
    fingerprint: str
    exact_hit: bool = False
    semantic_hit: bool = False
    similarity: Optional[float] = None
    latency_ms: float = 0.0
    provider_latency_ms: float = 0.0
    embedding_latency_ms: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    tokens_saved: int = 0
    estimated_cost_saved: float = 0.0
    response_source: ResponseSource = ResponseSource.LLM
