# Production Cloud Deployment Guide

**Target Environment**: AWS / Vercel / Kubernetes  
**Release Version**: v1.0.0  

---

## 1. Frontend Vercel Deployment
1. Connect GitHub repository to Vercel.
2. Set Root Directory to `frontend`.
3. Set Build Command to `npm run build` and Output Directory to `dist`.
4. Add Environment Variables:
   - `VITE_API_BASE_URL`: `https://api.aivisibility.com/api/v1`
5. Assign Custom Domain: `app.aivisibility.com` (Enforces HTTPS SSL via LetsEncrypt).

---

## 2. Backend AWS / Kubernetes Deployment
1. **Provision Infrastructure**:
   ```bash
   cd deploy/terraform
   terraform apply -auto-approve
   ```
2. **Execute Database Migrations**:
   ```bash
   alembic upgrade head
   ```
3. **Deploy Kubernetes Helm Chart**:
   ```bash
   cd deploy/helm
   helm upgrade --install ai-visibility . -f values.yaml --namespace production
   ```

---

## 3. Production Verification Protocol
1. Verify `/health` probe returns `{"status": "healthy"}`.
2. Verify `/ready` probe returns `{"status": "ready"}`.
3. Test end-to-end user registration, project creation, job execution, and report rendering.
