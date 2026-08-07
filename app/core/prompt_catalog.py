from typing import List
from app.schemas.prompt import PromptTemplate, PromptCategory

# Version-controlled, immutable canonical prompt catalog
PROMPT_CATALOG: List[PromptTemplate] = [
    PromptTemplate(
        id="PROMPT_DIRECT_V1",
        version="1.0.0",
        category=PromptCategory.DIRECT,
        template="What companies or software tools would you recommend for business domain {domain}?",
        description="Direct recommendation query evaluating top-of-mind brand awareness.",
        active=True
    ),
    PromptTemplate(
        id="PROMPT_COMPARISON_V1",
        version="1.0.0",
        category=PromptCategory.COMPARISON,
        template="Compare business domain {domain} versus top market competitors.",
        description="Comparative positioning query evaluating brand presence against competitors.",
        active=True
    ),
    PromptTemplate(
        id="PROMPT_USE_CASE_V1",
        version="1.0.0",
        category=PromptCategory.USE_CASE,
        template="What is the best software solution for business workflow and productivity involving {domain}?",
        description="Use-case solution query evaluating functional recommendation suitability.",
        active=True
    ),
    PromptTemplate(
        id="PROMPT_BUYING_V1",
        version="1.0.0",
        category=PromptCategory.BUYING,
        template="What software should a startup or growing business choose when considering {domain}?",
        description="Commercial buying intent query evaluating decision-stage recommendation inclusion.",
        active=True
    ),
]


def get_active_prompts() -> List[PromptTemplate]:
    """Returns all active prompt templates from the catalog."""
    return [p for p in PROMPT_CATALOG if p.active]
