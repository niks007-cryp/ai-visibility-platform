"""
Shared test helper: FakeGeminiProvider

A deterministic test double that implements query_structured() and query(),
returning well-formed structured JSON that the visibility scorer can parse.
Used by all tests that need execute_job() to succeed without a real API key.
"""
import json


FAKE_STRUCTURED_RESPONSE_TEMPLATE = """{{
  "brand": "{brand}",
  "domain": "{domain}",
  "queries": [
    {{
      "query_id": "category_recognition",
      "category": "category_recognition",
      "query": "What type of business does {brand} offer?",
      "response": "{brand} is a well-known business operating in its industry. It provides quality products and services to consumers.",
      "brand_mentioned": true,
      "brand_position": 1,
      "competitors_listed": [],
      "recommendation_strength": 3,
      "evidence_snippet": "{brand} is a well-known business"
    }},
    {{
      "query_id": "brand_recognition",
      "category": "brand_recognition",
      "query": "Which brands come to mind in the {brand} category?",
      "response": "In this category, {brand} is frequently mentioned alongside other leading brands.",
      "brand_mentioned": true,
      "brand_position": 1,
      "competitors_listed": ["CompetitorA", "CompetitorB"],
      "recommendation_strength": 4,
      "evidence_snippet": "{brand} is frequently mentioned"
    }},
    {{
      "query_id": "direct_recommendation",
      "category": "direct_recommendation",
      "query": "Can you recommend a service like {brand}?",
      "response": "Yes, {brand} is a strong recommendation for users seeking this type of service.",
      "brand_mentioned": true,
      "brand_position": 1,
      "competitors_listed": [],
      "recommendation_strength": 4,
      "evidence_snippet": "{brand} is a strong recommendation"
    }},
    {{
      "query_id": "use_case_fit",
      "category": "use_case_fit",
      "query": "Is {brand} a good choice for a consumer?",
      "response": "{brand} is well-suited for typical consumers and has a strong reputation.",
      "brand_mentioned": true,
      "brand_position": null,
      "competitors_listed": [],
      "recommendation_strength": 3,
      "evidence_snippet": "{brand} is well-suited"
    }},
    {{
      "query_id": "competitor_comparison",
      "category": "competitor_comparison",
      "query": "How does {brand} compare to competitors?",
      "response": "{brand} competes effectively with CompetitorA and CompetitorB in its space.",
      "brand_mentioned": true,
      "brand_position": null,
      "competitors_listed": ["CompetitorA", "CompetitorB"],
      "recommendation_strength": 2,
      "evidence_snippet": "{brand} competes effectively"
    }},
    {{
      "query_id": "brand_differentiation",
      "category": "brand_differentiation",
      "query": "What makes {brand} stand out?",
      "response": "{brand} differentiates itself through quality and reliability.",
      "brand_mentioned": true,
      "brand_position": null,
      "competitors_listed": [],
      "recommendation_strength": 3,
      "evidence_snippet": "{brand} differentiates itself"
    }},
    {{
      "query_id": "purchase_intent",
      "category": "purchase_intent",
      "query": "Where would you suggest shopping for what {brand} offers?",
      "response": "I would suggest visiting {brand} for purchasing this type of product or service.",
      "brand_mentioned": true,
      "brand_position": 1,
      "competitors_listed": [],
      "recommendation_strength": 4,
      "evidence_snippet": "visiting {brand} for purchasing"
    }},
    {{
      "query_id": "factual_knowledge",
      "category": "factual_knowledge",
      "query": "What do you know about {brand}?",
      "response": "{brand} is a recognized entity in its field, operating at {domain}.",
      "brand_mentioned": true,
      "brand_position": null,
      "competitors_listed": [],
      "recommendation_strength": 2,
      "evidence_snippet": "{brand} is a recognized entity"
    }}
  ]
}}"""


class FakeGeminiProvider:
    """
    Test double for GeminiProvider.
    Implements query_structured() and query() without making any API calls.
    Returns deterministic well-formed structured JSON for the given domain.
    """

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return "gemini-2.5-flash"

    async def query_structured(self, domain: str, brand_name=None) -> str:
        if not brand_name:
            clean = domain.lower().removeprefix("www.").split(".")[0]
            brand_name = clean.title()
        return FAKE_STRUCTURED_RESPONSE_TEMPLATE.format(
            brand=brand_name,
            domain=domain,
        )

    async def query(self, prompt: str, domain: str):
        from app.providers.base import ProviderOutput
        return ProviderOutput(
            provider_name=self.name,
            prompt=prompt,
            raw_response=f"Test Gemini response for {domain}. Prompt: {prompt}",
        )
