import asyncio
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
        return "gemini-2.5-flash"

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

        target_model = "gemini-2.5-flash"

        logger.info(
            "GEMINI_REQUEST provider=gemini model=%s domain=%s prompt_len=%d",
            target_model,
            domain,
            len(formatted_prompt),
        )

        try:
            client = genai.Client(api_key=self._api_key)

            async def _call_gemini_api():
                return await client.aio.models.generate_content(
                    model=target_model,
                    contents=formatted_prompt
                )

            response = await asyncio.wait_for(_call_gemini_api(), timeout=15.0)

            raw_text = getattr(response, "text", None)
            if not raw_text:
                raw_text = str(response)

            elapsed_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "GEMINI_RESPONSE provider=gemini model=%s domain=%s response_len=%d duration_ms=%.2f",
                target_model,
                domain,
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
                "GEMINI_ERROR provider=gemini model=%s error_type=TimeoutError error=timeout_15s",
                target_model,
            )
            raise GeminiAPIException(
                "Request to Gemini 2.5 Flash timed out after 15 seconds.",
                is_retryable=True,
            )

        except Exception as exc:
            err_msg = str(exc)
            err_type = type(exc).__name__

            logger.error(
                "GEMINI_ERROR provider=gemini model=%s error_type=%s error=%s",
                target_model,
                err_type,
                err_msg,
            )

            raise GeminiAPIException(
                err_msg,
                is_retryable="429" in err_msg or "503" in err_msg,
            )


gemini_provider = None
