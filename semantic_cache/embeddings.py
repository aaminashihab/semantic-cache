from abc import ABC, abstractmethod
from typing import List
import asyncio

class BaseEmbeddingModel(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass
        
    @abstractmethod
    async def aembed(self, text: str) -> List[float]:
        pass

class GeminiEmbedding(BaseEmbeddingModel):
    def __init__(self, model_name: str = "gemini-embedding-001"):
        try:
            from google import genai
            self.client = genai.Client()
        except ImportError:
            raise ImportError("Please install google-genai to use Gemini embeddings")
        self.model_name = model_name

    def embed(self, text: str) -> List[float]:
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
            config={"output_dimensionality": 768}
        )
        return response.embeddings[0].values

    async def aembed(self, text: str) -> List[float]:
        response = await self.client.aio.models.embed_content(
            model=self.model_name,
            contents=text,
            config={"output_dimensionality": 768}
        )
        return response.embeddings[0].values
