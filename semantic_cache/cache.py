import sqlite3
from typing import Optional, List
from datetime import datetime, timedelta
from .models import CacheRecord

class CacheDB:
    def __init__(self, db_path: str = "semantic_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(\"\"\"
                CREATE TABLE IF NOT EXISTS cache_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    faiss_id INTEGER,
                    prompt TEXT NOT NULL,
                    fingerprint TEXT NOT NULL UNIQUE,
                    response TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    temperature REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ttl INTEGER DEFAULT 0,
                    hit_count INTEGER DEFAULT 0,
                    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            \"\"\")
            conn.execute(\"\"\"
                CREATE INDEX IF NOT EXISTS idx_fingerprint ON cache_records(fingerprint)
            \"\"\")
            conn.execute(\"\"\"
                CREATE INDEX IF NOT EXISTS idx_faiss_id ON cache_records(faiss_id)
            \"\"\")

    def _is_expired(self, timestamp_str: str, ttl_days: int) -> bool:
        if ttl_days <= 0:
            return False
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return datetime.now() - timestamp > timedelta(days=ttl_days)

    def lookup_by_fingerprint(self, fingerprint: str, ttl_days: int = 0) -> Optional[CacheRecord]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM cache_records WHERE fingerprint = ?",
                (fingerprint,)
            ).fetchone()
            if row:
                if self._is_expired(row["timestamp"], ttl_days):
                    self.delete(row["id"])
                    return None
                return CacheRecord(**dict(row))
        return None

    def lookup_by_faiss_id(self, faiss_id: int, ttl_days: int = 0) -> Optional[CacheRecord]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM cache_records WHERE faiss_id = ?",
                (faiss_id,)
            ).fetchone()
            if row:
                if self._is_expired(row["timestamp"], ttl_days):
                    self.delete(row["id"])
                    return None
                return CacheRecord(**dict(row))
        return None

    def store(self, record: CacheRecord) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(\"\"\"
                INSERT INTO cache_records (
                    faiss_id, prompt, fingerprint, response, provider, model, temperature, ttl
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            \"\"\", (
                record.faiss_id, record.prompt, record.fingerprint, record.response,
                record.provider, record.model, record.temperature, record.ttl
            ))
            return cursor.lastrowid

    def update_faiss_id(self, record_id: int, faiss_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(\"\"\"
                UPDATE cache_records SET faiss_id = ? WHERE id = ?
            \"\"\", (faiss_id, record_id))

    def update_hit(self, record_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(\"\"\"
                UPDATE cache_records 
                SET hit_count = hit_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE id = ?
            \"\"\", (record_id,))
            
    def delete(self, record_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache_records WHERE id = ?", (record_id,))

    def evict_oldest(self, max_entries: int) -> List[int]:
        evicted_faiss_ids = []
        with sqlite3.connect(self.db_path) as conn:
            # Check count
            count = conn.execute("SELECT COUNT(*) FROM cache_records").fetchone()[0]
            if count > max_entries:
                limit = count - max_entries
                # Find oldest entries
                rows = conn.execute(
                    "SELECT id, faiss_id FROM cache_records ORDER BY timestamp ASC LIMIT ?",
                    (limit,)
                ).fetchall()
                for row in rows:
                    record_id, faiss_id = row[0], row[1]
                    if faiss_id is not None:
                        evicted_faiss_ids.append(faiss_id)
                    conn.execute("DELETE FROM cache_records WHERE id = ?", (record_id,))
        return evicted_faiss_ids
