# LLM Provider Engineering Guidelines

**AI Visibility Platform**  
**Author:** Principal AI Platform Engineer  
**Status:** Mandatory Engineering Standard (Locked)

---

## 1. Purpose

This document defines the strict architectural and operational standards for integrating Large Language Model (LLM) providers (Google Gemini, OpenAI ChatGPT, Anthropic Claude, Perplexity, DeepSeek, etc.) into the AI Visibility Platform.

All present and future LLM provider modules must strictly satisfy these guidelines before merging into `main`.

---

## 2. Provider Responsibilities

### Every Provider MUST:
- Inherit directly from `BaseProvider` (`app/providers/base.py`).
- Implement a unique canonical string `name` property (e.g. `"gemini"`, `"openai"`, `"claude"`).
- Execute queries asynchronously (`async def query(...)`).
- Return a standardized `ProviderOutput` object (`provider_name`, `prompt`, `raw_response`).
- Handle vendor-specific exceptions and map them to unified provider exceptions.
- Mask all API keys, bearer tokens, and sensitive headers in logs.

### Every Provider MUST NOT:
- Hardcode API keys, secrets, or endpoint URLs inside source code.
- Execute database operations or manipulate domain models.
- Perform UI rendering, report generation, or sentiment calculations.
- Block the main event loop with synchronous network I/O calls.
- Mutate global state or modify other provider instances.

---

## 3. `BaseProvider` Contract

### Design Philosophy
The `BaseProvider` abstract contract serves as an immutable boundary between vendor LLM SDKs and core application services. Core business logic depends ONLY on `BaseProvider`, enabling seamless vendor swapping and offline testing.

### Extension Rules
- Extensions must only add provider classes implementing `query(prompt, domain)`.
- Never modify the method signature of `BaseProvider.query()` to accommodate a specific vendor's proprietary API quirk.
- Vendor-specific payload transformations must occur encapsulated within the provider class adapter.

---

## 4. Prompt Standards

### Naming & Storage
- Prompts must be stored in centralized prompt templates, never inline within Python method strings.
- **Naming Convention**: `PROMPT_<CATEGORY>_<VERSION>` (e.g. `PROMPT_VISIBILITY_AUDIT_V1`).

### Prompt Versioning
- Every prompt used in production must carry an explicit version identifier (e.g. `v1.0`).
- Prompt changes require incrementing the version string to preserve historical audit reproducibility.

---

## 5. Model Standards

### Configuration Rule
- **NEVER hardcode model names** inside provider classes.
- Model names must be configured via environment settings (e.g., `GEMINI_MODEL`, `OPENAI_MODEL`).

### Fallback Defaults
- Each provider module must specify a sensible default model string in Pydantic Settings (e.g. `GEMINI_MODEL: str = "gemini-1.5-flash"`).

---

## 6. Configuration & Secrets

### Secret Handling
- All API keys must be loaded via `Pydantic Settings` (`app/core/config.py`).
- API keys must follow naming convention `<PROVIDER>_API_KEY` (e.g., `GEMINI_API_KEY`, `OPENAI_API_KEY`).
- Secret keys must NEVER be logged, committed to version control, or exposed in HTTP error payloads.

### Configuration Validation
- Provider initialization must validate API key presence. If unconfigured in environment, provider raises `ProviderNotConfiguredException`.

---

## 7. Error Handling

### Exception Classification

| Error Type | Category | Action | Example |
| :--- | :--- | :--- | :--- |
| **429 Rate Limit** | Retryable | Exponential Backoff (2 retries) | Gemini `ResourceExhausted` |
| **5xx Server Error** | Retryable | Exponential Backoff (2 retries) | OpenAI `ServiceUnavailable` |
| **401 / 403 Auth Error** | Non-Retryable | Fail immediately | Invalid API Key |
| **400 Bad Request** | Non-Retryable | Fail immediately | Prompt safety block / context overflow |
| **Timeout (15s)** | Retryable | Retry once or fail gracefully | Socket timeout / DeadlineExceeded |

---

## 8. Logging Standards

### Machine-Readable Structured Logs
Providers must emit key-value structured logs:
- `event=provider_query_start provider=gemini model=gemini-1.5-flash domain=acme.com`
- `event=provider_query_success provider=gemini domain=acme.com raw_length=482 latency_ms=820.5`
- `event=provider_query_error provider=gemini domain=acme.com error=rate_limit_exceeded`

---

## 9. Timeout & Retry Policy

### Timeout Policy
- Default timeout: **15.0 seconds** per API request.
- Enforced via `asyncio.wait_for(..., timeout=15.0)`.

### Retry Policy
- Maximum retries: **2 attempts**.
- Backoff schedule: `1.0s` initial delay, `2.0s` secondary delay with random jitter.
- Applies ONLY to retryable error categories (429 rate limits and 5xx server errors).

---

## 10. Response Storage

### What MUST Be Stored:
- `job_id`: FK reference to `AnalysisJob`.
- `provider_name`: Canonical string name.
- `prompt`: Submitted query text.
- `raw_response`: Unmodified, complete text response returned by the LLM.
- `created_at`: UTC timestamp.

### What MUST NEVER Be Stored in Provider Results:
- Raw API keys, bearer tokens, or HTTP request headers.
- Customer payment or sensitive personal data.

---

## 11. Testing Standards

### Automated CI/CD Environment
- CI pipelines execute 100% of tests using `MockProvider`.
- Live API calls are NEVER executed during automated CI builds to ensure deterministic, zero-cost tests.

### Live Integration Tests
- Integration tests targeting live LLM APIs require explicit opt-in flags (e.g. `pytest -m live_api`) and valid API keys in environment.

---

## 12. Future Provider Checklist

Before any PR introducing a new AI provider (OpenAI, Claude, Perplexity, etc.) is merged into `main`, it must satisfy this checklist:

- [ ] Inherits from `BaseProvider` and implements `name` and `query()`.
- [ ] Model name is configurable via environment variable (not hardcoded).
- [ ] API keys are securely parsed via Pydantic settings.
- [ ] Masks API keys in structured log output.
- [ ] Enforces 15s request timeout.
- [ ] Implements exponential retries for 429 rate limits.
- [ ] Unit tests pass with mock response fixtures.
- [ ] Registered cleanly without breaking existing providers.
