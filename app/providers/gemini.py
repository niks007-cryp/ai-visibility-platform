import asyncio
import logging
import time
from typing import Optional

import google.generativeai as genai

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


class GeminiProvider(BaseProvider):
    """Google Gemini AI Provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._model_name = model_name or settings.GEMINI_MODEL

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    async def query(
        self,
        prompt: str,
        domain: str,
    ) -> ProviderOutput:

        start_time = time.perf_counter()

        if self._api_key is None or self._api_key.strip() == "":
            logger.warning(
                "event=gemini_query_failed reason=api_key_missing domain=%s",
                domain,
            )
            raise GeminiNotConfiguredException()

        formatted_prompt = (
            f"Analyze visibility and recommendations for business website "
            f"'{domain}'. Query: {prompt}"
        )

        logger.info(
            "event=gemini_query_start domain=%s model=%s prompt_len=%d",
            domain,
            self._model_name,
            len(formatted_prompt),
        )

        try:
            genai.configure(api_key=self._api_key)

            model = genai.GenerativeModel(self._model_name)

            async def _call_gemini():
                return await model.generate_content_async(
                    formatted_prompt
                )

            response = await asyncio.wait_for(
                _call_gemini(),
                timeout=15.0,
            )

            raw_text = getattr(response, "text", None)

            if not raw_text:
                raw_text = str(response)

            elapsed_ms = (
                time.perf_counter() - start_time
            ) * 1000

            logger.info(
                "event=gemini_query_success "
                "domain=%s model=%s response_len=%d latency_ms=%.2f",
                domain,
                self._model_name,
                len(raw_text),
                elapsed_ms,
            )

            return ProviderOutput(
                provider_name=self.name,
                prompt=prompt,
                raw_response=raw_text,
            )

        except asyncio.TimeoutError:
            logger.error(
                "event=gemini_query_error domain=%s error=timeout_15s",
                domain,
            )

            raise GeminiAPIException(
                "Request to Gemini API timed out after 15 seconds.",
                is_retryable=True,
            )

        except Exception as exc:
            err_msg = str(exc)

            retryable_errors = (
                "429",
                "503",
                "ResourceExhausted",
            )

            is_retryable = any(
                error in err_msg
                for error in retryable_errors
            )

            logger.error(
                "event=gemini_query_error "
                "domain=%s error=%s retryable=%s",
                domain,
                err_msg,
                is_retryable,
            )

            raise GeminiAPIException(
                err_msg,
                is_retryable=is_retryable,
            )


# Do not instantiate at import time.
# Create GeminiProvider() where it is actually needed.
gemini_provider = None
