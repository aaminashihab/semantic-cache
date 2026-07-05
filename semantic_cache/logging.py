import sqlite3
from .models import RequestRecord

class RequestLogger:
    def __init__(self, db_path: str = "semantic_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS request_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    prompt TEXT,
                    fingerprint TEXT,
                    exact_hit BOOLEAN,
                    semantic_hit BOOLEAN,
                    similarity REAL,
                    latency_ms REAL,
                    provider_latency_ms REAL,
                    embedding_latency_ms REAL,
                    tokens_input INTEGER,
                    tokens_output INTEGER,
                    tokens_saved INTEGER,
                    estimated_cost_saved REAL,
                    response_source TEXT
                )
            """)

    def log(self, record: RequestRecord):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO request_logs (
                    prompt, fingerprint, exact_hit, semantic_hit, similarity, 
                    latency_ms, provider_latency_ms, embedding_latency_ms,
                    tokens_input, tokens_output, tokens_saved, estimated_cost_saved,
                    response_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.prompt, record.fingerprint, record.exact_hit, record.semantic_hit,
                record.similarity, record.latency_ms, record.provider_latency_ms,
                record.embedding_latency_ms, record.tokens_input, record.tokens_output,
                record.tokens_saved, record.estimated_cost_saved, record.response_source.value
            ))
