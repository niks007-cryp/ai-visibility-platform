# Production Rollback Guide

**Objective**: Rapidly restore operational service during severe production incidents.

---

## 1. Automated Kubernetes Rollback
To instantly rollback to the previous successful Helm release:
```bash
helm rollback ai-visibility 0 -n production
```

---

## 2. Docker Container Rollback
If deploying via raw Docker Compose:
```bash
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml pull ai-visibility-api:previous_tag
docker-compose -f docker-compose.production.yml up -d
```

---

## 3. Database Downgrade Migration
If the failed deployment included schema migrations:
```bash
alembic downgrade -1
```

---

## 4. Frontend Vercel Instant Rollback
1. Open Vercel Project Dashboard (`app.aivisibility.com`).
2. Navigate to **Deployments** tab.
3. Click **Instant Rollback** on the previous successful deployment.
