from typing import List
from app.schemas.prompt import PromptTemplate
from app.core.prompt_catalog import get_active_prompts


class PromptService:
    """Service layer managing prompt templates and active catalog access."""

    def list_active_prompts(self) -> List[PromptTemplate]:
        """Returns all active versioned prompt templates from the catalog."""
        return get_active_prompts()


prompt_service = PromptService()
