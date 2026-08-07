# DOMAIN.md — Business Domain Architecture

**AI Visibility Platform**  
**Author:** Lead Domain Architect  
**Status:** Canonical Domain Specification (Locked)

---

## 1. Purpose

This document establishes the official **Ubiquitous Language** and **Domain Architecture** for the AI Visibility Platform using Domain-Driven Design (DDD) principles.

It serves as the single source of truth for business terminology, entity boundaries, domain rules, and relationship lifecycles. Both product managers and software engineers must adhere strictly to the definitions and rules established in this document for all subsequent feature development.

---

## 2. Domain Overview

Traditional search engine optimization (SEO) measures business visibility on search engine result pages (SERPs) like Google. Modern customers increasingly ask Large Language Model (LLM) AI assistants—such as ChatGPT, Gemini, Claude, and Perplexity—for direct business, product, and service recommendations.

The **AI Visibility Platform** exists to help business owners understand, measure, and improve how their brand is cited and recommended inside conversational AI assistants. It removes technical complexity (such as prompt engineering, vector embeddings, and web scraping infrastructure) and transforms raw AI responses into actionable business guidance.

---

## 3. Core Business Question

Every feature in the system must serve to answer one central question:

> **"If a customer asks an AI assistant about my business or category, will it recommend me?"**

---

## 4. Domain Principles

1. **Business-First Naming**: Every domain concept must use terminology understood directly by non-technical business owners and marketers.
2. **Explicit Entity Boundaries**: One entity, one responsibility. Entities must never perform tasks outside their explicit domain boundary.
3. **Ubiquitous Language Consistency**: Software variable names, database models, API specs, and product documentation must use identical terms.
4. **Reports Over Raw Data**: Business owners do not want raw prompt outputs or complex charts; they want actionable conclusions and prioritized recommendations.
5. **Simplicity Over Cleverness**: Avoid premature abstractions. Model only domain concepts that directly answer the Core Business Question.

---

## 5. Ubiquitous Language

| Term | Domain Definition |
| :--- | :--- |
| **Project** | The root entity representing a specific business website registered for AI visibility auditing (e.g., `acmesoftware.io`). |
| **Analysis Job** | A discrete, tracked request to execute an AI visibility audit across targeted AI providers for a given Project. |
| **Provider** | An external AI assistant platform evaluated by the platform (e.g., OpenAI ChatGPT, Google Gemini, Anthropic Claude, Perplexity). |
| **Provider Result** | The raw and structured response captured from a single AI Provider for a specific query prompt during an Analysis Job. |
| **Analysis** | The synthesized calculation engine that evaluates all Provider Results for a job to compute score metrics and draw insights. |
| **Report** | The final, human-readable audit deliverable generated for a user after an Analysis completes. |
| **Recommendation** | A single, prioritized action item derived from a Report advising a business on how to improve its AI recommendation rate. |
| **Visibility Score** | A normalized metric (0% to 100%) indicating how consistently and favorably a Project is recommended by AI Providers. |
| **Prompt** | The specific question or query pattern submitted to AI Providers to test recommendation behavior (e.g., *"What are the best workflow tools for SaaS?"*). |
| **Execution** | The active phase during which an Analysis Job dispatches queries to Providers and records raw responses. |
| **Run** | An instance of an Analysis Job progressing through its lifecycle from creation to completion. |
| **History** | The chronological sequence of past Reports and Visibility Scores recorded for a Project over time. |
| **Status** | The current state of an Analysis Job (e.g., `Pending`, `Running`, `Completed`, `Failed`). |

---

## 6. Entities

### Project
- **Purpose**: Represents a business website entity whose AI visibility is monitored.
- **Responsibilities**: Holds target domain attributes, name, and serves as the anchor for all audit runs.
- **Relationships**: Parent to zero or more Analysis Jobs.
- **Lifecycle**: Created → Active → Updated → Archived / Deleted.

### Analysis Job
- **Purpose**: Tracks the lifecycle of an audit run request.
- **Responsibilities**: Manages execution state, records progress status, timestamping, and failure reasons if applicable.
- **Relationships**: Belongs to exactly one Project; parent to Provider Results and one Report.
- **Lifecycle**: Pending → Running → Completed (or Failed).

### Provider Result
- **Purpose**: Captures raw AI provider response evidence for audit queries.
- **Responsibilities**: Stores raw response text, citation sources, recommendation rank position, and provider metadata.
- **Relationships**: Belongs to exactly one Analysis Job; belongs to one Provider category.
- **Lifecycle**: Created upon provider query return → Immutable.

### Analysis
- **Purpose**: Processing unit that synthesizes multiple Provider Results into business insights.
- **Responsibilities**: Calculates the overall Visibility Score, identifies competitive share, and derives strengths/weaknesses.
- **Relationships**: Consumes Provider Results → Produces exactly one Report.
- **Lifecycle**: Executed immediately after Provider Results are collected → Transient.

### Report
- **Purpose**: The core user-facing deliverable presenting AI visibility findings.
- **Responsibilities**: Holds overall score, provider breakdown, narrative qualitative summary, and recommendations list.
- **Relationships**: Belongs to exactly one Analysis Job; parent to multiple Recommendations.
- **Lifecycle**: Generated → Published → Stored in Project History (Immutable).

### Recommendation
- **Purpose**: An actionable business improvement step designed to boost AI visibility.
- **Responsibilities**: Holds priority level (High, Medium, Low), rationale ("Why it matters"), step-by-step fix guide, and impact estimate.
- **Relationships**: Belongs to exactly one Report.
- **Lifecycle**: Derived → Active → Completed by User.

---

## 7. Entity Relationships & Execution Flow

```
[Project]
   │
   └── (1:N) ──> [Analysis Job]
                    │
                    ├── (1:N) ──> [Provider Result]
                    │                  │
                    │                  ▼
                    └── (1:1) ──> [Analysis Engine]
                                       │
                                       ▼
                                   [Report]
                                       │
                                       └── (1:N) ──> [Recommendation]
```

### Flow Rationale
1. A **Project** represents the customer's website.
2. When an audit is requested, an **Analysis Job** is queued to track the lifecycle of the audit run.
3. The job queries multiple AI **Providers**, producing **Provider Results** containing raw AI response evidence.
4. The **Analysis Engine** evaluates all collected Provider Results to calculate the normalized **Visibility Score** and identify weaknesses.
5. The analysis produces a single **Report**, which contains a prioritized list of actionable **Recommendations**.

---

## 8. Domain Rules

1. **Project Domain Uniqueness**: A Project is uniquely identified by its clean root domain (e.g. `example.com`). Duplicate Projects for the same domain are strictly prohibited.
2. **Analysis Job Isolation**: An Analysis Job belongs to exactly one Project. Provider Results cannot exist without an associated Analysis Job.
3. **Report Immutability**: Once a Report is generated and published, it is immutable to preserve historical audit accuracy.
4. **Recommendation Derivation**: Recommendations must be explicitly derived from evidence contained within Provider Results and cannot be generated arbitrarily.
5. **Score Boundaries**: Visibility Scores are normalized integers between 0 and 100 inclusive.

---

## 9. Future Expansion

The following domain concepts may be integrated in future phases without breaking the existing core domain model:
- **Competitor**: Benchmark brand entity associated with a Project to compare recommendation share.
- **Prompt Template**: Custom prompt patterns configured per Project or industry vertical.
- **Trend Snapshot**: Aggregated historical metrics comparing sequential Reports over time.

---

## 10. Out of Scope (Postponed Capabilities)

The following capabilities are explicitly **OUT OF SCOPE** for the current domain phase and must NOT be added to entities or APIs yet:

- ❌ Billing & Subscriptions
- ❌ Organizations & Teams
- ❌ User Roles & Fine-Grained Permissions
- ❌ Multi-Tenant Workspaces
- ❌ Background Task Queues (Celery/Redis)
- ❌ Scheduled / Automated Recurring Audits
- ❌ API Key Management
- ❌ Webhooks & Notification Channels (Email/Slack)

---

## 11. Business Source of Truth

This specification is the canonical domain model. Any pull request or schema change that violates the entity boundaries, domain rules, or ubiquitous language in this document must be rejected.
