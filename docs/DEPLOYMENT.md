# Deployment Guide

## Overview

Ledger-bot deploys automatically to staging when changes are merged to `main` branch.

## Deployment Flow

1. Developer merges PR to `main` branch in `ledger-bot-app` repository
2. GitHub Actions runs tests
3. GitHub Actions builds Docker image and pushes to ECR
4. GitHub Actions updates `eks-app-workloads/workloads/ledger-bot/values.staging.yaml` with new image tag
5. ArgoCD detects change in `eks-app-workloads` and deploys to staging EKS cluster
6. Pod starts, health checks pass, bot connects to Slack

## Manual Deployment Steps (First Time Only)

### 1. Update Secrets

Replace placeholder secrets with actual values:

```bash
cd ~/IdeaProjects/eks-app-workloads/workloads/ledger-bot
sops secrets.staging.yaml
# Replace PLACEHOLDER values with actual tokens
```

### 2. Submit PR to eks-app-workloads

```bash
cd ~/IdeaProjects/eks-app-workloads
git checkout -b add-ledger-bot-workload
git add workloads/ledger-bot/
git commit -m "feat: add ledger-bot workload configuration"
git push origin add-ledger-bot-workload
# Create PR in GitHub
```

### 3. Merge PR

Once PR is approved and merged, ArgoCD will automatically deploy to staging.

### 4. Verify Deployment

```bash
# Check pod status
kubectl get pods -n ledger-bot -l app=ledger-bot

# Check pod logs
kubectl logs -n ledger-bot -l app=ledger-bot --tail=50

# Check health endpoints
kubectl port-forward -n ledger-bot svc/ledger-bot 8080:8080
curl http://localhost:8080/health
curl http://localhost:8080/ready
```

### 5. Test in Slack

Send a direct message to @ledgerbot in Slack:
"What is GL Publisher?"

Expected: Bot responds with information from knowledge base

## Updating the Bot

After first deployment, updates are automatic:

1. Merge code changes to `main` branch in `ledger-bot-app`
2. CI/CD pipeline automatically builds, pushes, and updates eks-app-workloads
3. ArgoCD deploys new version to staging

## Troubleshooting

### Pod Not Starting

```bash
kubectl describe pod -n ledger-bot -l app=ledger-bot
kubectl logs -n ledger-bot -l app=ledger-bot
```

Common issues:
- Missing or invalid secrets (check SLACK_BOT_TOKEN, SLACK_APP_TOKEN, LITELLM_DEVELOPER_KEY)
- Image pull errors (verify ECR permissions)
- Resource limits too low (check memory/CPU usage)

### Health Checks Failing

```bash
kubectl get events -n ledger-bot
```

Common issues:
- Port 8080 not accessible (check HEALTH_PORT env var)
- App not starting (check logs for Python errors)

### Bot Not Responding in Slack

1. Check pod is running: `kubectl get pods -n ledger-bot`
2. Check logs: `kubectl logs -n ledger-bot -l app=ledger-bot`
3. Verify tokens are correct in secrets
4. Check Slack Socket Mode connection in logs

## Rollback

If new deployment has issues:

```bash
cd ~/IdeaProjects/eks-app-workloads
git revert HEAD
git push origin main
```

ArgoCD will automatically deploy previous version.
