# Engineering Sprint Retrospectives

**AI Visibility Platform**  
**Author:** Lead AI Platform Engineer  
**Document Purpose:** Chronicling engineering lessons, technical debt tracking, architectural retrospective reviews, and sprint recommendations.

---

## Sprint 4 Retrospective

### 1. What Went Well?
- **Zero Contract Changes**: The `BaseProvider` contract designed in Sprint 3 accommodated `GeminiProvider` with **zero modifications** to existing domain contracts or models.
- **Zero-Cost Automated Testing**: `MockProvider` allowed our entire test suite (23 tests) to pass in under 9 seconds without making live, paid cloud API calls or failing CI runs when API keys are absent.
- **Secret Hygiene**: `pydantic-settings` isolated `GEMINI_API_KEY` handling safely, guaranteeing API keys are never printed in logs or committed to version control.
- **Engineering Standards**: `docs/LLM_PROVIDER_GUIDELINES.md` established explicit guidelines for prompt versioning, secret masking, and 15s timeout enforcement.

---

### 2. What Technical Debt Was Introduced?
- **Single-Provider Execution Parameter**: `AnalysisJobService.execute_job()` currently takes a single `provider: Optional[BaseProvider] = None` parameter. To query multiple AI assistants concurrently (Gemini + OpenAI + Claude), this parameter must be updated to accept a collection of target providers.
- **SDK Deprecation Warning**: Google emitted a deprecation warning on `google.generativeai` recommending future migration to `google.genai`.

---

### 3. What Should Be Refactored Before Sprint 6?
- **Concurrent Multi-Provider Query Execution**: Update `AnalysisJobService.execute_job()` to accept a list of active `BaseProvider` targets and execute queries concurrently using `asyncio.gather()`.
- **Response Evidence Parser**: Create an evidence parsing helper module to extract domain mention status, rank position, and sentiment from raw provider text responses.

---

### 4. What Engineering Decisions Aged Well?
- **Radical Architect Simplification in Sprint 3**: Stripping out `ProviderFactory` and `ProviderManager` early kept the codebase clean. Adding `GeminiProvider` required creating only one focused file ([`app/providers/gemini.py`](file:///C:/Users/nits4/.gemini/antigravity-ide/scratch/ai-visibility-platform/app/providers/gemini.py)).
- **Row-Level Database Locking**: `select(AnalysisJob).with_for_update()` inside `AnalysisJobRepository` reliably prevents active job race conditions.

---

### 5. What Assumptions May Become Future Problems?
- **Synchronous HTTP Job Execution**: Executing queries directly inside the HTTP request lifecycle works for single mock/Gemini calls. However, as we query 3+ AI models simultaneously (Gemini, OpenAI, Claude), combined latency will exceed 3–5 seconds, reinforcing the need for background task queues (Celery/Redis or FastAPI background tasks).

---

### 6. System Status & Roadmap Update
- **`ROADMAP.md`**: Updated to mark Sprint 4 complete and position Sprint 5 for OpenAI & Claude multi-provider integration.
- **`TASKS.md`**: Updated with completed Sprint 4 tasks and defined upcoming Sprint 5 checklist items.

---

### 7. Recommended Next Sprint
**Sprint 5 — Multi-Provider AI Execution (OpenAI + Claude + Concurrent Dispatch)**
- Integrate `OpenAIProvider` (`gpt-4o`) and `ClaudeProvider` (`claude-3-5-sonnet`) implementing `BaseProvider`.
- Update `AnalysisJobService` to execute queries across all active providers concurrently via `asyncio.gather()`.
