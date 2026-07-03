import faiss
import numpy as np
from typing import List, Tuple, Optional

class VectorStore:
    def __init__(self, dimension: int, index_path: str = "faiss_index.bin"):
        self.dimension = dimension
        self.index_path = index_path
        self.index = faiss.IndexIDMap(faiss.IndexFlatIP(dimension))
        self.load()

    def _normalize_vector(self, vector: List[float]) -> np.ndarray:
        v = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(v)
        if norm > 0:
            v = v / norm
        return v

    def add(self, vector: List[float], record_id: int):
        v = self._normalize_vector(vector).reshape(1, -1)
        ids = np.array([record_id], dtype=np.int64)
        self.index.add_with_ids(v, ids)

    def search(self, vector: List[float], top_k: int = 1) -> List[Tuple[int, float]]:
        if self.index.ntotal == 0:
            return []
        v = self._normalize_vector(vector).reshape(1, -1)
        distances, indices = self.index.search(v, top_k)
        
        results = []
        for i in range(top_k):
            if indices[0][i] != -1:
                results.append((int(indices[0][i]), float(distances[0][i])))
        return results

    def remove(self, ids: List[int]):
        if not ids:
            return
        id_array = np.array(ids, dtype=np.int64)
        self.index.remove_ids(id_array)

    def next_id(self) -> int:
        # Just use a simple incrementing counter based on current size, 
        # or simply max ID + 1. But since we delete, max ID + 1 is safer.
        # However, IndexIDMap doesn't expose max ID easily, so we maintain it or generate random int64.
        # Actually, simpler is to use a timestamp-based ID or uuid-based int64.
        import time
        return int(time.time() * 1000000) % (2**63 - 1)

    def save(self):
        faiss.write_index(self.index, self.index_path)

    def load(self):
        import os
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
