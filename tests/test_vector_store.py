import pytest
import os
from semantic_cache.vector_store import VectorStore

@pytest.fixture
def vector_store():
    index_path = "test_faiss.bin"
    if os.path.exists(index_path):
        os.remove(index_path)
    store = VectorStore(dimension=3, index_path=index_path)
    yield store
    if os.path.exists(index_path):
        os.remove(index_path)

def test_vector_store_add_and_search(vector_store):
    vector1 = [1.0, 0.0, 0.0]
    vector2 = [0.0, 1.0, 0.0]
    
    vector_store.add(vector1, 1)
    vector_store.add(vector2, 2)
    
    results = vector_store.search([1.0, 0.0, 0.0], top_k=1)
    assert len(results) == 1
    assert results[0][0] == 1
    # IP of normalized [1,0,0] and [1,0,0] is 1.0
    assert results[0][1] > 0.99

def test_vector_store_save_load(vector_store):
    vector_store.add([0.0, 0.0, 1.0], 3)
    vector_store.save()
    
    new_store = VectorStore(dimension=3, index_path=vector_store.index_path)
    results = new_store.search([0.0, 0.0, 1.0], top_k=1)
    
    assert len(results) == 1
    assert results[0][0] == 3
