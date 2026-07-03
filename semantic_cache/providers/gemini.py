from .base import BaseProvider
import asyncio

class GeminiProvider(BaseProvider):
    def __init__(self, model: str = "gemini-2.5-flash"):
        try:
            from google import genai
            self.client = genai.Client()
        except ImportError:
            raise ImportError("Please install google-genai to use Gemini provider")
        self._model = model

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        from google.genai import types
        config = types.GenerateContentConfig(temperature=temperature)
        response = self.client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=config
        )
        return response.text

    async def agenerate(self, prompt: str, temperature: float = 0.7) -> str:
        from google.genai import types
        config = types.GenerateContentConfig(temperature=temperature)
        response = await self.client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=config
        )
        return response.text

    def count_tokens(self, text: str) -> int:
        response = self.client.models.count_tokens(
            model=self._model,
            contents=text
        )
        return response.total_tokens
        
    async def acount_tokens(self, text: str) -> int:
        # Since google-genai aio.models.count_tokens might not be available or 
        # behaves identically, we wrap the sync call if async is unavailable.
        # It's fast enough typically, but let's attempt async.
        try:
            response = await self.client.aio.models.count_tokens(
                model=self._model,
                contents=text
            )
            return response.total_tokens
        except AttributeError:
            # Fallback
            return await asyncio.to_thread(self.count_tokens, text)

    def model_name(self) -> str:
        return self._model
