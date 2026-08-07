# Production Emergency Runbooks & Incident Response

---

## Runbook 1: PostgreSQL Database Failure / Failover
**Symptom**: `/ready` probe returns `503 Service Unavailable` with database error.
1. Check RDS multi-AZ failover status in AWS Console / CLI:
   ```bash
   aws rds describe-db-instances --db-instance-identifier ai-visibility-prod
   ```
2. Verify connection pool metrics at `/metrics`.
3. If primary database is unresponsive, trigger manual RDS failover:
   ```bash
   aws rds reboot-db-instance --db-instance-identifier ai-visibility-prod --force-failover
   ```

---

## Runbook 2: Background Task Queue Backlog
**Symptom**: Alert `QueueBacklogHigh` triggered (Queue depth > 100).
1. Inspect worker telemetry:
   ```bash
   curl -f http://app.aivisibility.com/api/v1/worker/health
   ```
2. Scale worker Kubernetes deployment to 10 replicas:
   ```bash
   kubectl scale deployment ai-visibility-worker --replicas=10 -n production
   ```

---

## Runbook 3: Secret Rotation Procedure
1. Update secret in AWS Secrets Manager:
   ```bash
   aws secretsmanager update-secret --secret-id ai-visibility/jwt-secret --secret-string "NewSuperStrongSecretKey2026!"
   ```
2. Restart API deployment to pick up rotated secret:
   ```bash
   kubectl rollout restart deployment/ai-visibility-api -n production
   ```
