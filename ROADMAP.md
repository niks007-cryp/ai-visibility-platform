# ROADMAP.md — 12-Month Product & Engineering Roadmap

**AI Visibility Platform**  
**Version:** 2.0 (Post-Sprint 6 Strategy Pivot)  
**Status:** Locked Canonical Execution Plan  

---

## Completed Milestones (Foundational Platform)

- [x] **Sprint 0: Core Infrastructure Setup**
  - Python 3.12, FastAPI, Async SQLAlchemy 2.0, PostgreSQL, Alembic, pytest suite, `/health` endpoint.
- [x] **Sprint 1: Project Domain**
  - `projects` schema, domain normalization, `ProjectRepository`, `ProjectService`, CRUD endpoints.
- [x] **Sprint 2: Analysis Job Domain**
  - `analysis_jobs` schema, `JobStateMachine` (`Pending → Running → Completed`), atomic `FOR UPDATE` concurrency guard.
- [x] **Sprint 3: Provider Abstraction & MockProvider**
  - `BaseProvider` contract, `MockProvider` for zero-cost offline testing, `provider_results` schema & repository.
- [x] **Sprint 4: Live Gemini Provider**
  - `GeminiProvider` (`gemini-1.5-flash`), `GEMINI_API_KEY` settings, 15s timeout, raw response persistence.
- [x] **Sprint 5: Evidence Extraction Engine**
  - `extracted_evidence` schema, stateless extractors (`BrandMentionExtractor`, `CitationExtractor`, `SnippetExtractor`), `EvidencePipeline`.
- [x] **Sprint 6: MVP Report API**
  - Single read-only `GET /api/v1/jobs/{job_id}/report` endpoint assembling existing entities into frontend-ready DTO.

---

## Phase 1: MVP Release & PLG Launch (Months 1–3)

- [ ] **Sprint 7: Lightweight Frontend Web App**
  - Modern, responsive SPA interface displaying domain setup form, async job progress bar, and MVP report view.
- [ ] **Sprint 8: Closed-Loop Remediation Engine (Action Plan)**
  - Rule-based remediation planner generating top 3 prioritized action items (e.g. *"Publish vs-competitor comparison page"*).
- [ ] **Sprint 9: Multi-LLM Provider Matrix**
  - Add `OpenAIProvider` (`gpt-4o`) and `ClaudeProvider` (`claude-3-5-sonnet`) implementing `BaseProvider`.
  - Parallel multi-provider dispatch via `asyncio.gather()`.

---

## Phase 2: Growth & Continuous Monitoring (Months 4–6)

- [ ] **Sprint 10: Background Worker Queue (Celery/Redis)**
  - Transition inline HTTP job execution to distributed background worker tasks for high-concurrency scaling.
- [ ] **Sprint 11: Scheduled Weekly Audits & Email Alerts**
  - Cron-scheduled weekly re-audits with email notification alerts upon AI recommendation status change.
- [ ] **Sprint 12: Competitor Share-of-Voice Benchmarking**
  - Multi-domain comparative visibility scoring matrix against top 3 market competitors.

---

## Phase 3: Closed-Loop Verification & Scale (Months 7–12)

- [ ] **Sprint 13: Autonomous Fix Verification Pipeline**
  - Scheduled 14-day post-publication re-audit verifying if AI models updated recommendations.
- [ ] **Sprint 14: Agency Multi-Tenant Workspaces**
  - Multi-tenant client management, custom PDF report export, and white-label branding.
- [ ] **Sprint 15: Public Developer API & CMS Plugins**
  - Public REST API with API key authentication, rate-limiting, and Webflow/WordPress sync plugins.
