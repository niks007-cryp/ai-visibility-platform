# TASKS.md — Task Tracker

**Current Sprint:** Sprint 4 (Completed & Merged)  
**Next Sprint:** Sprint 5 (OpenAI & Claude Provider Integrations)

---

## Completed Tasks

### Sprint 0
- [x] Python 3.12 + FastAPI project setup with `uv`
- [x] Dockerfile & Docker Compose with PostgreSQL 16
- [x] Async SQLAlchemy 2.0 & Alembic setup
- [x] Structured JSON logging & pytest configuration
- [x] Health & readiness check endpoint (`/health` & `/api/v1/health`)

### Sprint 1
- [x] `projects` table database migration
- [x] Domain validation & normalization logic (`extract_clean_domain`)
- [x] ProjectRepository & ProjectService implementation
- [x] Thin Project CRUD API endpoints
- [x] Pytest suite for Project management

### Sprint 2
- [x] `analysis_jobs` table database migration with composite index
- [x] Dedicated `JobStateMachine` with allowed transition matrix
- [x] Atomic concurrent active job guard (`with_for_update`)
- [x] AnalysisJobRepository & AnalysisJobService implementation
- [x] API endpoints for job creation, listing, status fetch, and cancellation
- [x] Structured event logging with timing

### Sprint 3
- [x] Abstract `BaseProvider` contract & `ProviderOutput` dataclass
- [x] `MockProvider` implementation for offline testing
- [x] `provider_results` table database migration & repository
- [x] Service layer integration for provider execution
- [x] Unit and integration tests for MockProvider

### Sprint 4
- [x] Created `docs/LLM_PROVIDER_GUIDELINES.md` engineering standards
- [x] Added `google-generativeai` dependency and configuration settings
- [x] Implemented `GeminiProvider` (`gemini-1.5-flash`, 15s timeout, secret masking)
- [x] Persistence of raw Gemini responses to `provider_results`
- [x] Unit & integration tests for `GeminiProvider` (100% pass rate)

---

## Upcoming Tasks (Sprint 5)

- [ ] Add `OPENAI_API_KEY` & `OPENAI_MODEL` settings to `app/core/config.py`
- [ ] Implement `OpenAIProvider` (`app/providers/openai.py`) implementing `BaseProvider`
- [ ] Add `CLAUDE_API_KEY` & `CLAUDE_MODEL` settings to `app/core/config.py`
- [ ] Implement `ClaudeProvider` (`app/providers/claude.py`) implementing `BaseProvider`
- [ ] Enable parallel multi-provider execution in `AnalysisJobService.execute_job()`
- [ ] Pytest suite for multi-provider query execution
