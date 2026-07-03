from pydantic import BaseModel, Field

class CacheConfig(BaseModel):
    # These strings will only be used if DI isn't provided directly
    provider: str = "gemini"
    model: str = "gemini-2.5-flash"
    similarity_threshold: float = 0.92
    db_path: str = "semantic_cache.db"
    index_path: str = "semantic_cache.faiss"
    vector_dim: int = 768
    embedding_model: str = "text-embedding-004"
    enable_metrics: bool = True
    log_requests: bool = True
    ttl_days: int = 30
    max_entries: int = 100000
