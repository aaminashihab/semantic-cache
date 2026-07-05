import os
import asyncio
import logging
from typing import Optional
from .base import BaseProvider

logger = logging.getLogger(__name__)

class GeminiProvider(BaseProvider):
    def __init__(
        self, 
        model: str = "gemini-2.5-flash", 
        api_key: Optional[str] = None,
        cost_per_input_token: float = 0.0,
        cost_per_output_token: float = 0.0
    ):
        try:
            from google import genai
            key = api_key or os.environ.get("GEMINI_API_KEY")
            self.client = genai.Client(api_key=key)
        except ImportError:
            raise ImportError("Please install google-genai to use Gemini provider")
            
        self._model = model
        self._cost_in = cost_per_input_token
        self._cost_out = cost_per_output_token
        
        if self._cost_in == 0.0 and self._cost_out == 0.0:
            logger.warning("GeminiProvider initialized with 0.0 cost rates. Savings will report as $0.")

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
        
    @property
    def cost_per_input_token(self) -> float:
        return self._cost_in

    @property
    def cost_per_output_token(self) -> float:
        return self._cost_out
