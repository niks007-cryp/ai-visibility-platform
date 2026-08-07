from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderOutput:
    """Standardized output data structure from an AI provider query."""
    provider_name: str
    prompt: str
    raw_response: str


class BaseProvider(ABC):
    """Abstract Base Class establishing the contract for AI Providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the canonical string name of the provider."""
        pass

    @abstractmethod
    async def query(self, prompt: str, domain: str) -> ProviderOutput:
        """Executes a query prompt against the provider for a domain."""
        pass
