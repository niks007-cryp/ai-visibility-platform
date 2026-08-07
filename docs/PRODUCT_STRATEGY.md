# Company Blueprint & Product Strategy — AI Visibility Platform

**Company Blueprint**  
**Role:** Founder, Chief Product Officer, Principal Software Architect & GTM Strategist  
**Classification:** Venture-Backed SaaS Product & Engineering Blueprint  
**Status:** Locked Canonical Document  

---

## 1. Product Vision
To become the definitive enterprise system of record for Generative Engine Optimization (GEO) and Answer Engine Optimization (AEO), enabling businesses to measure, optimize, and control how AI assistants recommend their brand.

---

## 2. Mission
Eliminate AI recommendation obscurity for business leaders by delivering transparent AI audits, deterministic evidence, and closed-loop optimization workflows that directly drive customer acquisition.

---

## 3. Positioning Statement
For B2B SaaS founders, marketing teams, and growth leaders who struggle to understand why AI assistants (Google Gemini, ChatGPT, Claude) omit or misrepresent their product:

> **The AI Visibility Platform is the only closed-loop GEO engine that turns AI recommendation audits into step-by-step fix guides and verified business outcomes.**

Unlike passive monitoring tools (such as Peppertype or BrightEdge AEO) that only provide dashboard charts and arbitrary scores, our platform closes the loop from **Insight → Implementation → Verification**.

---

## 4. Target Customer Profile (ICP)

### Primary ICP: B2B SaaS Founders & Marketing Leads (10–200 Employees)
- **Pain Point**: Prospects tell them *"I asked ChatGPT for the top software in your space, and it recommended your competitor instead of you."*
- **Budget**: $99 – $499/month marketing & SEO tool budget.
- **Buying Trigger**: Realization that Google Search traffic is decaying while LLM search queries are accelerating.

### Secondary ICP: Digital Marketing & SEO Agencies
- **Pain Point**: Clients demanding AI visibility reports; agencies currently hacking together manual ChatGPT prompts and spreadsheets.
- **Budget**: $499 – $1,499/month agency tier.

---

## 5. Jobs To Be Done (JTBD)

1. **Proof of AI Presence**: *"When a prospective buyer asks AI about software in my category, I need to know if my brand is recommended."*
2. **Root Cause Analysis**: *"If AI omits my company, I need to know exact missing sources, citations, or positioning gaps."*
3. **Actionable Remediation**: *"I need a prioritized, step-by-step checklist telling my team exactly what content or citations to publish to fix our AI visibility."*
4. **Verification of Fixes**: *"After publishing new content, I need to verify that AI assistants updated their recommendations."*

---

## 6. Core Product Pillars

1. **Deterministic Evidence Engine**: Every score and status is backed by observable, verifiable raw text quotes and URL citations—never black-box hallucinations.
2. **Closed-Loop Remediation**: We don't just report problems; we supply step-by-step content and citation blueprints that solve them.
3. **Multi-Model Intelligence Matrix**: Aggregated audit across Google Gemini, OpenAI ChatGPT, Anthropic Claude, and Perplexity.
4. **Instant Time-to-Value**: Zero-configuration domain submission delivering a complete audit report in under 30 seconds.

---

## 7. Competitive Advantages

| Feature Category | Competitors (15–20 Players) | Our Platform |
| :--- | :--- | :--- |
| **Focus** | Passive Monitoring & Charts | **Closed-Loop Fix & Verification** |
| **Methodology** | Proprietary Black-Box Scores | **100% Deterministic Evidence** |
| **User Experience** | Complex, technical SEO dashboards | **2-Click Executive Summary** |
| **Verification** | None (Manual re-runs) | **Automated Fix Verification Pipeline** |

---

## 8. What We WILL NOT Build

- ❌ **Generic Content Generators**: We will not build low-quality AI blog post spammers.
- ❌ **Traditional Google Keyword Trackers**: We will not compete with Semrush/Ahrefs on traditional 10-blue-link Google SERPs.
- ❌ **Social Media Listening**: We will not monitor Twitter/LinkedIn sentiment.
- ❌ **Custom Enterprise Professional Services**: We build scalable self-serve software, not manual consulting agencies.

---

## 9. MVP Scope (Sprint 0–6)

- **Domain Submission**: 2-click setup (`POST /api/v1/projects`).
- **Async Job Execution**: Concurrency-guarded state machine (`Pending → Running → Completed`).
- **Provider Layer**: Live Google Gemini integration (`gemini-1.5-flash`) + `MockProvider` for zero-cost offline testing.
- **Evidence Extraction**: Deterministic extraction of domain mentions, URL citations, matching quotes, and competitor tokens.
- **Unified MVP Report API**: Read-only `GET /api/v1/jobs/{job_id}/report` endpoint returning single frontend-ready JSON payload.

---

## 10. V2 Roadmap (Months 3–6)

- **Multi-LLM Matrix**: Parallel audit dispatch across OpenAI (`gpt-4o`), Anthropic (`claude-3-5-sonnet`), and Perplexity.
- **Closed-Loop Action Plan**: Prioritized step-by-step content & citation remediation playbook.
- **Continuous Monitoring & Alerts**: Weekly automated AI re-audits with email alerts when AI recommendation status changes.
- **Competitor Share-of-Voice Matrix**: Comparative side-by-side brand visibility scores against top 3 competitors.

---

## 11. V3 Roadmap (Months 7–12)

- **Autonomous Verification Pipeline**: Re-audits AI assistants automatically 14 days after content publication to confirm recommendation update.
- **CMS & Knowledge Base Integrations**: One-click sync with WordPress, Webflow, and HubSpot.
- **Agency Multi-Tenant Workspaces**: Client management, custom PDF exports, and white-label reporting.
- **Enterprise API Access**: Public REST API for programmatic GEO audits.

---

## 12. Pricing Strategy

- **Starter ($49/mo)**: 1 Domain, 10 Audits/mo, Single-LLM (Gemini), Email support.
- **Pro ($149/mo)**: 3 Domains, 50 Audits/mo, Multi-LLM Matrix (Gemini + OpenAI + Claude), Closed-Loop Action Plan, Weekly Monitoring.
- **Agency ($499/mo)**: 15 Domains, 300 Audits/mo, White-Label PDF Reports, Competitor Share-of-Voice, Dedicated Support.

---

## 13. Go-To-Market (GTM) Strategy

1. **Product-Led Growth (PLG)**: Free 1-click AI Visibility Audit tool on our homepage.
2. **Weekly "AI Visibility Index" Reports**: Benchmark audits of top 50 SaaS categories (e.g. *"Who dominates AI search in CRM?"*) published as viral industry research.
3. **Agency Partner Program**: Free agency tier for SEO agencies to generate AI audit lead magnets for their clients.
4. **Founder Outreach**: Direct cold outreach targeting SaaS founders with a screenshot of their AI recommendation omission.

---

## 14. Technical Moats

- **Deterministic Extraction Pipeline**: High-throughput, stateless regex and parsing pipeline that processes raw LLM responses into structured evidence in < 5ms.
- **Concurrency-Guarded State Machine**: Production-grade async pipeline built on FastAPI and Async SQLAlchemy preventing duplicate jobs and race conditions under scale.

---

## 15. Data Moats

- **Historical AI Citation Index**: Proprietary database tracking which third-party websites (G2, Capterra, Reddit, TechCrunch) AI assistants cite most frequently per software category over time.

---

## 16. AI Moats

- **Provider-Agnostic LLM Layer**: Unified `BaseProvider` abstraction enabling seamless model switching and instant integration of new LLM models (e.g. DeepSeek, Grok) within hours of release.

---

## 17. Long-Term Vision (3–5 Years)

To become the standard platform where every company manages their digital presence across AI models, search engines, and autonomous AI agents.

---

## 18. Success Metrics

- **ARR / MRR Growth**: Target $1M ARR in Month 12.
- **Audit Volume**: > 100,000 completed AI visibility audits per month.
- **Fix Verification Rate**: > 40% of users who implement our action plans verify improved AI recommendations within 30 days.
- **Net Revenue Retention (NRR)**: > 110%.

---

## 19. Product Principles

1. **Evidence Before Opinion**: Every insight must be grounded in observable raw text quotes and citations.
2. **Action Over Analytics**: Never show a chart without providing the direct step-by-step action to improve it.
3. **Simplicity Wins**: Executive summaries first; technical deep-dives on demand.

---

## 20. Engineering Principles

1. **Freeze Core Domains**: Protect core models (`Project`, `AnalysisJob`) from bloat.
2. **Async By Default**: All I/O and network operations must use non-blocking async Python.
3. **Deterministic Pipeline**: Fact extraction must be 100% reproducible.

---

## 21. UX Principles

1. **2-Click Value**: User inputs domain and gets executive report in under 30 seconds.
2. **Zero Setup Friction**: No API keys required for end users.
3. **Visual Clarity**: Green/Amber/Red visibility badges with clear explanations.

---

## 22. Risks & Mitigation

- **Risk 1: AI Provider Rate Limits / API Costs**:
  - *Mitigation*: Multi-model routing, prompt token optimization, and intelligent caching of raw responses.
- **Risk 2: LLM Non-Determinism**:
  - *Mitigation*: Multi-query sampling and deterministic evidence parsing across responses.

---

## 23. Key Unknowns Requiring Customer Validation

1. *Will marketing teams pay $149/mo specifically for GEO, or do they expect it integrated into traditional SEO tools?*
2. *Which third-party sources (e.g. Reddit vs G2 vs comparison blogs) have the highest impact on shifting LLM recommendations?*
3. *What is the optimal re-audit frequency (weekly vs bi-weekly) that aligns with LLM index update speeds?*
