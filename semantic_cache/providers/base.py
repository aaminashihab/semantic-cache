from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        pass

    @abstractmethod
    async def agenerate(self, prompt: str, temperature: float = 0.7) -> str:
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass
        
    @abstractmethod
    async def acount_tokens(self, text: str) -> int:
        pass

    @abstractmethod
    def model_name(self) -> str:
        pass
