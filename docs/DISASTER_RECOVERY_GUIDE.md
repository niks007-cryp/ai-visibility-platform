# Production Disaster Recovery Guide

**SLA Targets**:
- **Recovery Time Objective (RTO)**: < 15 Minutes
- **Recovery Point Objective (RPO)**: < 5 Minutes

---

## 1. Database Automated Point-in-Time Restore (AWS RDS)
1. List available snapshots:
   ```bash
   aws rds describe-db-snapshots --db-instance-identifier ai-visibility-prod
   ```
2. Restore snapshot to new instance:
   ```bash
   aws rds restore-db-instance-from-db-snapshot \
     --db-instance-identifier ai-visibility-prod-restored \
     --db-snapshot-identifier rds:ai-visibility-prod-2026-08-08-00-00
   ```
3. Update `DATABASE_URL` secret in AWS Secrets Manager and restart pods.

---

## 2. Redis Cluster Flush & Queue Reset
If Redis queue or cache state is corrupted:
```bash
redis-cli -h redis.internal.aivisibility.com FLUSHALL
kubectl rollout restart deployment/ai-visibility-worker -n production
```
