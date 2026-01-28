# Production Infrastructure Design

**Date:** 2026-01-27
**Status:** Approved
**Phase:** Phase 1 - Staging Infrastructure Setup

## Overview

Design for making ledger-bot production-ready by integrating with Wealthsimple's existing EKS/ArgoCD infrastructure. Starting with staging environment only, with production and monitoring to be added in future phases.

## Context

Ledger-bot is currently a prototype with basic Kubernetes manifests but not integrated into Wealthsimple's deployment infrastructure. It needs proper CI/CD, secrets management, and deployment automation to be operationally viable.

## Key Infrastructure Components

### 1. Existing Wealthsimple Infrastructure

- **EKS Cluster:** Managed Kubernetes with ArgoCD for GitOps deployments
- **Container Registry:** AWS ECR at `526316940316.dkr.ecr.us-east-1.amazonaws.com`
- **Deployment Config:** `eks-app-workloads` repository with Helm charts
- **Secrets:** SOPS-encrypted secrets with AWS KMS
- **CI/CD:** GitHub Actions with `wealthsimple/github-workflows` reusable actions

### 2. CI/CD Pipeline

**Location:** `ledger-bot-app/.github/workflows/default.yml`

**Workflow:**
1. Trigger on every push to any branch
2. Run pytest tests
3. Build Docker image using existing Dockerfile
4. On main branch: Push to ECR with commit SHA as tag
5. Auto-update `eks-app-workloads` with new image tag

**Image naming:** `526316940316.dkr.ecr.us-east-1.amazonaws.com/wealthsimple/ledger-bot:<commit-sha>`

**Key patterns:**
- Uses `wealthsimple/github-workflows@v1` actions
- Requires AWS IAM role assumption for ECR access
- Parallel multi-region ECR login (us-east-1, ca-central-1)

### 3. Workload Configuration

**Location:** `eks-app-workloads/workloads/ledger-bot/`

**Files:**
- `Chart.yaml` - Helm chart dependencies (ws-service chart)
- `values.staging.yaml` - Staging environment configuration
- `secrets.staging.yaml` - SOPS-encrypted secrets

**Configuration highlights:**
- **Replicas:** 1 (Socket Mode limitation - single connection)
- **Resources:** 500m CPU request, 512Mi memory
- **Health checks:** `/health` (liveness), `/ready` (readiness)
- **Port:** 8080 for health checks
- **Owner:** BOR Write team (@bor-write-eng)

**Secrets:**
- `SLACK_BOT_TOKEN` - Bot user OAuth token
- `SLACK_APP_TOKEN` - App-level token for Socket Mode
- `LITELLM_DEVELOPER_KEY` - LiteLLM API key

### 4. Deployment Flow

```
Developer merges PR
    ↓
GitHub Actions workflow triggered
    ↓
Tests run (pytest)
    ↓
Docker image built
    ↓
Image pushed to ECR (tagged with commit SHA)
    ↓
CI automation updates eks-app-workloads
    ↓
ArgoCD detects change in eks-app-workloads
    ↓
ArgoCD deploys to staging EKS cluster
    ↓
Pod starts, health checks pass
    ↓
Bot connects to Slack via Socket Mode
```

## Design Decisions

### Why Staging Only First?
- Validate deployment process before production
- Test with limited user base (BOR Write team)
- Iterate on configuration without production risk
- Lower stakes for learning EKS/ArgoCD patterns

### Why ws-service Helm Chart?
- Standard Wealthsimple pattern for all services
- Handles common concerns: secrets, health checks, service accounts, RBAC
- Consistent with existing workloads
- Well-documented and supported

### Why Socket Mode (Single Replica)?
- Slack's Socket Mode requires single persistent connection
- Cannot horizontally scale
- Simpler than webhook-based approach (no ingress needed)
- Acceptable for staging/beta deployment

### Why Skip Monitoring Initially?
- Faster path to deployment
- Can add incrementally once deployed
- Health checks provide basic observability
- Kubernetes logs available via kubectl

## Implementation Tasks

1. **Create CI/CD pipeline** in ledger-bot-app repository
2. **Create workload configuration** in eks-app-workloads repository
3. **Encrypt secrets** using SOPS
4. **Test rendering** with `just render ledger-bot staging`
5. **Submit PRs** to both repositories
6. **Deploy to staging** via ArgoCD
7. **Verify deployment** - pod running, bot responding in Slack

## Future Phases

### Phase 2: Production Environment
- Add `values.production.yaml` and `secrets.production.yaml`
- Promotion workflow from staging to production
- Production-specific resource limits and owner configuration

### Phase 3: Monitoring & Observability
- Prometheus metrics endpoint (`/metrics`)
- Grafana dashboards
- Alerting rules (pod crashes, error rates)
- Structured JSON logging

### Phase 4: Operational Support
- Runbook for common issues
- On-call procedures
- SLA/SLO definitions
- Rate limiting implementation
- Cost tracking and budgets

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Socket Mode single point of failure | Brief downtime on pod restart | Acceptable for staging; document for users |
| Secrets misconfiguration | Bot won't start | Test locally before deployment |
| Resource limits too low | Pod OOM killed | Start conservative, monitor, adjust |
| First time using ArgoCD | Deployment issues | Follow existing workload patterns closely |
| CI/CD pipeline failures | No deployments | Test workflow in PR, validate ECR access |

## Success Criteria

- ✅ Docker image automatically built and pushed to ECR on main branch merge
- ✅ ArgoCD successfully deploys ledger-bot to staging
- ✅ Pod passes health checks and stays running
- ✅ Bot connects to Slack and responds to messages
- ✅ No manual deployment steps required after initial setup

## References

- [eks-app-workloads README](https://github.com/wealthsimple/eks-app-workloads)
- [ws-service Helm Chart](https://github.com/wealthsimple/helm-charts/blob/main/charts/ws-service/README.md)
- [SOPS Secrets Management](https://www.notion.so/wealthsimple/How-To-Manage-secrets-SOPS-21c41167bd96808da955c4621714f917)
- Example workload: `eks-app-workloads/workloads/auth-service`

## Approval

**Design approved by:** Kayla Lu
**Date:** 2026-01-27
**Next step:** Create implementation plan
