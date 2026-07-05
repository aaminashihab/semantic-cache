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
        
    @property
    @abstractmethod
    def cost_per_input_token(self) -> float:
        pass

    @property
    @abstractmethod
    def cost_per_output_token(self) -> float:
        pass
