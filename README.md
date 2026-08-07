# AI Visibility Operating System (v1.0.0)

[![CI Pipeline](https://github.com/aivisibility/ai-visibility-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/aivisibility/ai-visibility-platform/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version: 1.0.0](https://img.shields.io/badge/Version-1.0.0-blue.svg)](https://github.com/aivisibility/ai-visibility-platform/releases/tag/v1.0.0)

> **Enterprise AI Visibility & Answer Engine Optimization (AEO) Platform**.  
> Track, evaluate, and optimize how Generative AI engines (Gemini, ChatGPT, Claude) recommend your brand.

---

## ⚡ Key Capabilities

- **Stateless Evidence Extraction Engine**: Pure fact extraction (citations, sentence quotes, competitor mentions). Zero LLM hallucinations.
- **Deterministic Recommendation Engine**: Rule-based remediation generator mapping observable evidence to P0/P1/P2 actionable tasks.
- **Version-Controlled Prompt Evaluation Framework**: Evaluates domains across 4 canonical prompt categories (`DIRECT`, `COMPARISON`, `USE_CASE`, `BUYING`).
- **Confidence & Consistency Engine**: Telemetry module calculating multi-prompt execution consistency (P95 SLA) and detecting prompt contradictions.
- **Asynchronous Task Queue & Worker Infrastructure**: Decoupled background execution powered by Redis and standalone worker containers.
- **Production Hardened & Multi-Tenant**: PBKDF2-HMAC-SHA256 authentication, signed JWT tokens, rate limiting (5 req/min on auth), and owner resource isolation.

---

## 🚀 Quickstart (Local Development)

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/aivisibility/ai-visibility-platform.git
cd ai-visibility-platform
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .[dev]
```

### 2. Run Test Suite
```bash
pytest
```
*Output: 62 passed in 2.85s*

### 3. Run Local Stack via Docker Compose
```bash
docker-compose -f docker-compose.production.yml up --build
```

Access services:
- **Frontend SPA**: `http://localhost:5173` or `http://localhost:3000`
- **Backend REST API Docs**: `http://localhost:8000/docs`
- **Health Probes**: `http://localhost:8000/health`
- **Prometheus Metrics**: `http://localhost:8000/metrics`

---

## 🌐 Production Environment Variables

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Target environment mode | `production` |
| `DATABASE_URL` | Async PostgreSQL Connection String | `postgresql+asyncpg://user:pass@db:5432/aivisibility` |
| `REDIS_URL` | Redis Broker URL | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT Signing Key (Must be set in production) | `e.g. 64-char hex secret` |
| `GEMINI_API_KEY` | Google Gemini API Key | `AIzaSy...` |

---

## 📚 Documentation & Runbooks

- 📖 [Beta Launch Operating Playbook](file:///docs/BETA_LAUNCH_PLAYBOOK.md)
- 🔒 [Production Deployment Guide](file:///docs/PRODUCTION_DEPLOYMENT_GUIDE.md)
- 🚨 [Emergency Incident Runbooks](file:///docs/RUNBOOKS.md)
- 🛠️ [Rollback & Recovery Guide](file:///docs/ROLLBACK_GUIDE.md)
- 📋 [Final Architecture Audit Report](file:///docs/FINAL_ARCHITECTURE_AUDIT.md)

---

## 📄 License
Released under the [MIT License](LICENSE).
