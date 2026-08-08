import asyncio
import json
import logging
import time
from typing import Optional

from google import genai

from app.core.config import settings
from app.providers.base import BaseProvider, ProviderOutput

logger = logging.getLogger("app.providers.gemini")


class GeminiNotConfiguredException(Exception):
    """Raised when GEMINI_API_KEY is missing."""

    def __init__(self):
        super().__init__(
            "GEMINI_API_KEY is not configured in application settings."
        )


class GeminiAPIException(Exception):
    """Raised when the Gemini API returns an error."""

    def __init__(self, message: str, is_retryable: bool = False):
        self.is_retryable = is_retryable
        super().__init__(f"Gemini API Error: {message}")


# ── Structured prompt template (1 request, 8 evaluation dimensions) ────────────

STRUCTURED_VISIBILITY_PROMPT = """\
You are an AI visibility analysis engine. Your task is to evaluate how a specific brand/domain appears in AI-generated answers across 8 standardized evaluation dimensions.

Brand/Domain under analysis: {brand_name} ({domain})

For each of the 8 queries below, respond as a knowledgeable AI assistant would respond to that query — then provide a structured evaluation of whether and how the brand appeared in your response.

Queries to evaluate:
1. [category_recognition] What type of business or service does {brand_name} offer?
2. [brand_recognition] When someone asks for recommendations in the {brand_name} category, which brands come to mind?
3. [direct_recommendation] Can you recommend a website or service for someone looking for what {brand_name} offers?
4. [use_case_fit] Is {brand_name} a good choice for a typical consumer looking for this type of product or service?
5. [competitor_comparison] How does {brand_name} compare to its main competitors?
6. [brand_differentiation] What makes {brand_name} stand out from alternatives in its space?
7. [purchase_intent] If someone asked you where to shop or find services like {brand_name}, what would you suggest?
8. [factual_knowledge] What factual information do you know about {brand_name} and what it offers?

Return ONLY a valid JSON object in this exact schema. Do not include any text outside the JSON:

{{
  "brand": "{brand_name}",
  "domain": "{domain}",
  "queries": [
    {{
      "query_id": "category_recognition",
      "category": "category_recognition",
      "query": "What type of business or service does {brand_name} offer?",
      "response": "<your actual AI response to this query>",
      "brand_mentioned": true,
      "brand_position": 1,
      "competitors_listed": [],
      "recommendation_strength": 3,
      "evidence_snippet": "<exact quote from response that mentions the brand>"
    }},
    {{
      "query_id": "brand_recognition",
      "category": "brand_recognition",
      "query": "When someone asks for recommendations in the {brand_name} category, which brands come to mind?",
      "response": "<your actual AI response to this query>",
      "brand_mentioned": true,
      "brand_position": 1,
      "competitors_listed": ["Competitor A", "Competitor B"],
      "recommendation_strength": 4,
      "evidence_snippet": "<exact quote>"
    }},
    {{
      "query_id": "direct_recommendation",
      "category": "direct_recommendation",
      "query": "Can you recommend a website or service for someone looking for what {brand_name} offers?",
      "response": "<your actual AI response>",
      "brand_mentioned": true,
      "brand_position": 1,
      "competitors_listed": [],
      "recommendation_strength": 4,
      "evidence_snippet": "<exact quote>"
    }},
    {{
      "query_id": "use_case_fit",
      "category": "use_case_fit",
      "query": "Is {brand_name} a good choice for a typical consumer?",
      "response": "<your actual AI response>",
      "brand_mentioned": true,
      "brand_position": null,
      "competitors_listed": [],
      "recommendation_strength": 3,
      "evidence_snippet": "<exact quote>"
    }},
    {{
      "query_id": "competitor_comparison",
      "category": "competitor_comparison",
      "query": "How does {brand_name} compare to its main competitors?",
      "response": "<your actual AI response>",
      "brand_mentioned": true,
      "brand_position": null,
      "competitors_listed": ["Competitor A"],
      "recommendation_strength": 2,
      "evidence_snippet": "<exact quote>"
    }},
    {{
      "query_id": "brand_differentiation",
      "category": "brand_differentiation",
      "query": "What makes {brand_name} stand out from alternatives?",
      "response": "<your actual AI response>",
      "brand_mentioned": true,
      "brand_position": null,
      "competitors_listed": [],
      "recommendation_strength": 3,
      "evidence_snippet": "<exact quote>"
    }},
    {{
      "query_id": "purchase_intent",
      "category": "purchase_intent",
      "query": "Where would you suggest to shop for what {brand_name} offers?",
      "response": "<your actual AI response>",
      "brand_mentioned": true,
      "brand_position": 2,
      "competitors_listed": ["Competitor A"],
      "recommendation_strength": 3,
      "evidence_snippet": "<exact quote>"
    }},
    {{
      "query_id": "factual_knowledge",
      "category": "factual_knowledge",
      "query": "What factual information do you know about {brand_name}?",
      "response": "<your actual AI response>",
      "brand_mentioned": true,
      "brand_position": null,
      "competitors_listed": [],
      "recommendation_strength": 2,
      "evidence_snippet": "<exact quote>"
    }}
  ]
}}

Rules for filling in the schema:
- "response": Write your actual AI answer to that query as you would normally respond.
- "brand_mentioned": true only if {brand_name} or {domain} appears in your response.
- "brand_position": integer position (1=first mentioned, 2=second, etc.) or null if not mentioned.
- "competitors_listed": list of competitor brand names you mentioned in your response.
- "recommendation_strength": 0=not recommended, 1=weak, 2=moderate, 3=clear, 4=strong, 5=top recommendation.
- "evidence_snippet": exact quoted text from your response where the brand appears, or empty string if not mentioned.
"""


class GeminiProvider(BaseProvider):
    """Google Gemini AI Provider using official google-genai SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._model_name = model_name or settings.GEMINI_MODEL or "gemini-2.5-flash"

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    def _require_api_key(self, domain: str) -> None:
        if not self._api_key or not self._api_key.strip():
            logger.warning(
                "event=gemini_query_failed reason=api_key_missing domain=%s", domain
            )
            raise GeminiNotConfiguredException()

    async def query_structured(
        self,
        domain: str,
        brand_name: Optional[str] = None,
    ) -> str:
        """
        ONE Gemini API request covering 8 standardized visibility dimensions.

        Returns raw JSON string. Caller is responsible for parsing and scoring.
        Raises GeminiAPIException on any Gemini-side failure.
        Does NOT fall back to mock data.
        """
        self._require_api_key(domain)

        if not brand_name:
            # Extract brand name from domain: "www.myntra.com" → "Myntra"
            clean = domain.lower().removeprefix("www.").split(".")[0]
            brand_name = clean.title()

        prompt = STRUCTURED_VISIBILITY_PROMPT.format(
            brand_name=brand_name,
            domain=domain,
        )

        target_model = "gemini-2.5-flash"

        logger.info(
            "GEMINI_REQUEST provider=gemini model=%s domain=%s brand=%s "
            "prompt_len=%d request_count=1",
            target_model, domain, brand_name, len(prompt),
        )
        start_time = time.perf_counter()

        try:
            client = genai.Client(api_key=self._api_key)

            async def _call():
                return await client.aio.models.generate_content(
                    model=target_model,
                    contents=prompt,
                )

            response = await asyncio.wait_for(_call(), timeout=40.0)

            raw_text = getattr(response, "text", None) or str(response)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "GEMINI_RESPONSE provider=gemini model=%s domain=%s "
                "response_len=%d duration_ms=%.2f request_count=1",
                target_model, domain, len(raw_text), elapsed_ms,
            )
            return raw_text

        except asyncio.TimeoutError:
            logger.error(
                "GEMINI_ERROR provider=gemini model=%s error_type=timeout domain=%s",
                target_model, domain,
            )
            raise GeminiAPIException(
                "Request to Gemini 2.5 Flash timed out after 40 seconds.",
                is_retryable=True,
            )

        except Exception as exc:
            err_msg = str(exc)
            err_type = type(exc).__name__
            logger.error(
                "GEMINI_ERROR provider=gemini model=%s error_type=%s error=%s domain=%s",
                target_model, err_type, err_msg, domain,
            )
            raise GeminiAPIException(
                err_msg,
                is_retryable="429" in err_msg or "503" in err_msg,
            )

    async def query(
        self,
        prompt: str,
        domain: str,
    ) -> ProviderOutput:
        """
        Legacy single-prompt query. Kept for backward compatibility with tests.
        Not used in the production pipeline (query_structured is used instead).
        """
        self._require_api_key(domain)

        target_model = "gemini-2.5-flash"
        logger.info(
            "GEMINI_REQUEST provider=gemini model=%s domain=%s prompt_len=%d",
            target_model, domain, len(prompt),
        )
        start_time = time.perf_counter()

        try:
            client = genai.Client(api_key=self._api_key)

            async def _call():
                return await client.aio.models.generate_content(
                    model=target_model,
                    contents=prompt,
                )

            response = await asyncio.wait_for(_call(), timeout=40.0)
            raw_text = getattr(response, "text", None) or str(response)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "GEMINI_RESPONSE provider=gemini model=%s domain=%s "
                "response_len=%d duration_ms=%.2f",
                target_model, domain, len(raw_text), elapsed_ms,
            )
            return ProviderOutput(
                provider_name=self.name,
                prompt=prompt,
                raw_response=raw_text,
            )

        except asyncio.TimeoutError:
            raise GeminiAPIException(
                "Request to Gemini 2.5 Flash timed out after 40 seconds.",
                is_retryable=True,
            )
        except Exception as exc:
            err_msg = str(exc)
            raise GeminiAPIException(
                err_msg,
                is_retryable="429" in err_msg or "503" in err_msg,
            )


gemini_provider = None
