# Production Cloud Deployment Guide

---

## 1. Prerequisites
- **Terraform** >= 1.5.0
- **AWS CLI** v2 authenticated
- **kubectl** & **Helm** v3

---

## 2. Infrastructure Provisioning
```bash
cd deploy/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

---

## 3. Database Migration
```bash
# Run Alembic migrations against production PostgreSQL
alembic upgrade head
```

---

## 4. Kubernetes Helm Deployment
```bash
cd deploy/helm
helm upgrade --install ai-visibility . -f values.yaml --namespace production --create-namespace
```

---

## 5. Deployment Verification
```bash
kubectl get pods -n production
curl -f https://app.aivisibility.com/ready
```
