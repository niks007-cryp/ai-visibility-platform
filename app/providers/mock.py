from app.providers.base import BaseProvider, ProviderOutput


class MockProvider(BaseProvider):
    """In-memory Mock Provider for offline execution, testing, and development."""

    @property
    def name(self) -> str:
        return "mock"

    async def query(self, prompt: str, domain: str) -> ProviderOutput:
        response_text = (
            f"Simulated AI recommendation analysis for target domain '{domain}'. "
            f"Query prompt: '{prompt}'. Status: Domain is cited as a key recommendation."
        )
        return ProviderOutput(
            provider_name=self.name,
            prompt=prompt,
            raw_response=response_text
        )


mock_provider = MockProvider()
