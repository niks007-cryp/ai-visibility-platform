# MVP_DEFINITION.md — Canonical MVP Scope Specification

**AI Visibility Platform**  
**Version:** 2.0 (Post-Sprint 6 Alignment)  
**Status:** Locked Canonical Document  

---

## 1. Product Vision & MVP Objective

Build the simplest and most trustworthy platform that answers one core business question:

> **"If someone asks an AI about my business, will it recommend me?"**

The MVP focuses exclusively on **speed to value**, converting a raw domain URL into a complete AI visibility report in under **30 seconds**.

---

## 2. Target Customer

- **Primary User**: B2B SaaS Founders, Growth Leads, and Marketing Managers.
- **Problem Solved**: Lack of visibility into whether AI search engines (like Google Gemini) recommend their brand or omit them in favor of competitors.

---

## 3. Included vs. Excluded Scope

### INCLUDED in MVP (Sprint 0–8):
- **Project Domain Setup**: 2-click project registration (`POST /api/v1/projects`).
- **Async Job Engine**: Concurrency-guarded state machine (`Pending → Running → Completed`).
- **AI Provider**: Google Gemini (`gemini-1.5-flash`) + `MockProvider` for zero-cost offline testing.
- **Evidence Extraction**: Deterministic extraction of brand presence, URL citations, sentence quotes, and competitor brand mentions.
- **Unified MVP Report API**: Read-only `GET /api/v1/jobs/{job_id}/report` returning single frontend payload.
- **Action Plan**: Top 3 prioritized remediation action items.
- **Minimalist Web UI**: Single-page web dashboard displaying audit results.

### EXCLUDED from MVP:
- ❌ Multi-provider matrix (OpenAI/Claude postponed to Phase 2).
- ❌ Stripe billing and credit card paywalls.
- ❌ Teams, multi-tenant agency workspaces, and user roles.
- ❌ Competitor share-of-voice comparison charts.
- ❌ Background worker queues (Celery/Redis postponed to Phase 2).
- ❌ Scheduled weekly automated cron re-audits.
- ❌ Public REST API keys.

---

## 4. Definition of MVP Complete

The MVP is complete when:
1. User enters domain URL (e.g. `acmesoftware.io`).
2. System creates Project, triggers Analysis Job, and queries Gemini API (or MockProvider in dev).
3. System extracts raw evidence deterministically and stores `ExtractedEvidence`.
4. System returns unified MVP Report payload (`JobReportResponse`).
5. Web interface displays Visibility Status, raw evidence quotes, and top 3 action items.
6. Automated pytest suite passes 100%.
