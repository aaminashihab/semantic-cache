import pytest
from unittest.mock import MagicMock, AsyncMock
import os
import asyncio
from semantic_cache import SemanticCache
from semantic_cache.providers.base import BaseProvider
from semantic_cache.embeddings import BaseEmbeddingModel

class MockProvider(BaseProvider):
    def generate(self, prompt, temperature=0.7):
        return "Mocked Response"
    async def agenerate(self, prompt, temperature=0.7):
        return "Mocked Response"
    def count_tokens(self, text): return 10
    async def acount_tokens(self, text): return 10
    def model_name(self): return "mock-model"
    @property
    def cost_per_input_token(self): return 0.001
    
    @property
    def cost_per_output_token(self): return 0.002

class MockEmbedding(BaseEmbeddingModel):
    def embed(self, text): return [0.1] * 768
    async def aembed(self, text): return [0.1] * 768

@pytest.fixture
def mock_cache():
    db_path = "test_engine.db"
    index_path = "test_engine.faiss"
    if os.path.exists(db_path): os.remove(db_path)
    if os.path.exists(index_path): os.remove(index_path)
        
    provider = MockProvider()
    provider.generate = MagicMock(return_value="Mocked Response")
    provider.agenerate = AsyncMock(return_value="Mocked Async Response")
    
    cache = SemanticCache(
        provider=provider,
        embedding_model=MockEmbedding(),
        similarity_threshold=0.9,
        db_path=db_path,
        index_path=index_path
    )
    
    yield cache
    
    if os.path.exists(db_path): os.remove(db_path)
    if os.path.exists(index_path): os.remove(index_path)

def test_cache_miss_and_hit(mock_cache):
    response1 = mock_cache.generate("Hello world")
    assert response1 == "Mocked Response"
    mock_cache.provider.generate.assert_called_once()
    
    mock_cache.provider.generate.reset_mock()
    response2 = mock_cache.generate("Hello world")
    assert response2 == "Mocked Response"
    mock_cache.provider.generate.assert_not_called()
    
    mock_cache.provider.generate.reset_mock()
    response3 = mock_cache.generate("Hello world!")
    assert response3 == "Mocked Response"
    mock_cache.provider.generate.assert_not_called()

@pytest.mark.asyncio
async def test_cache_async(mock_cache):
    # Call agenerate
    resp1 = await mock_cache.agenerate("Async hello")
    assert resp1 == "Mocked Async Response"
    mock_cache.provider.agenerate.assert_called_once()
    
    # Exact hit async
    mock_cache.provider.agenerate.reset_mock()
    resp2 = await mock_cache.agenerate("Async hello")
    assert resp2 == "Mocked Async Response"
    mock_cache.provider.agenerate.assert_not_called()
