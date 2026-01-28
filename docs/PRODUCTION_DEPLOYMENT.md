# Ledger Bot - Production Deployment Guide

**Current State:** Running locally on your laptop (`python app.py`)

**Goal:** Production-ready service with proper infrastructure, monitoring, and support

---

## Table of Contents
1. [Pre-Production Checklist](#pre-production-checklist)
2. [Deployment Options](#deployment-options)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Security Hardening](#security-hardening)
5. [Monitoring & Observability](#monitoring--observability)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Testing Strategy](#testing-strategy)
8. [Support & On-Call](#support--on-call)
9. [Rollout Plan](#rollout-plan)

---

## Pre-Production Checklist

### Code Quality
- [ ] Add tests (unit + integration)
- [ ] Code review by team
- [ ] Linting/formatting (black, flake8)
- [ ] Type hints added
- [ ] Error handling improved
- [ ] Logging added throughout

### Documentation
- [ ] README complete
- [ ] Architecture diagram
- [ ] API documentation
- [ ] Runbook for on-call
- [ ] Incident response plan

### Security
- [ ] Secrets in proper secret manager
- [ ] No hardcoded credentials
- [ ] Dependencies scanned (Snyk/Dependabot)
- [ ] Security review completed
- [ ] Rate limiting implemented

### Performance
- [ ] Load testing completed
- [ ] Response time benchmarks
- [ ] Resource requirements defined
- [ ] Scaling strategy planned

---

## Deployment Options

### Option 1: Kubernetes (Recommended for Wealthsimple)

**Pros:**
- ✅ Standard company infrastructure
- ✅ Auto-scaling, self-healing
- ✅ Easy rollbacks
- ✅ Integrated with monitoring

**Cons:**
- ⚠️ More complex setup
- ⚠️ Requires k8s knowledge

**Best for:** Long-term production deployment

### Option 2: Cloud Run / App Engine

**Pros:**
- ✅ Serverless (pay per use)
- ✅ Auto-scaling
- ✅ Simple deployment

**Cons:**
- ⚠️ Cold start latency
- ⚠️ May require company approval

**Best for:** Quick MVP deployment

### Option 3: VM / EC2 with systemd

**Pros:**
- ✅ Simple and direct
- ✅ Full control

**Cons:**
- ❌ Manual scaling
- ❌ No auto-restart (need systemd)
- ❌ Manual updates

**Best for:** Small-scale or testing

**Recommendation:** Use Kubernetes if available at Wealthsimple.

---

## Infrastructure Setup

### Kubernetes Deployment

**1. Create Dockerfile**

```dockerfile
# /Users/kayla.lu/ledger-bot-app/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY knowledge_base.txt .

# Copy shared library if using hybrid architecture
COPY gl_publisher_knowledge/ ./gl_publisher_knowledge/

# Run as non-root user
RUN useradd -m -u 1000 ledgerbot
USER ledgerbot

CMD ["python", "app.py"]
```

**2. Create Kubernetes manifests**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ledger-bot
  namespace: bor-write
  labels:
    app: ledger-bot
spec:
  replicas: 2  # High availability
  selector:
    matchLabels:
      app: ledger-bot
  template:
    metadata:
      labels:
        app: ledger-bot
    spec:
      containers:
      - name: ledger-bot
        image: gcr.io/wealthsimple/ledger-bot:latest
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        env:
        - name: SLACK_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: ledger-bot-secrets
              key: slack-bot-token
        - name: SLACK_APP_TOKEN
          valueFrom:
            secretKeyRef:
              name: ledger-bot-secrets
              key: slack-app-token
        - name: LITELLM_DEVELOPER_KEY
          valueFrom:
            secretKeyRef:
              name: ledger-bot-secrets
              key: litellm-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

```yaml
# k8s/secret.yaml (use sealed-secrets or vault)
apiVersion: v1
kind: Secret
metadata:
  name: ledger-bot-secrets
  namespace: bor-write
type: Opaque
data:
  slack-bot-token: <base64-encoded>
  slack-app-token: <base64-encoded>
  litellm-key: <base64-encoded>
```

**3. Add health check endpoints**

Update `app.py`:

```python
# Add Flask app for health checks
from flask import Flask, jsonify

health_app = Flask(__name__)

@health_app.route('/health')
def health():
    """Liveness probe - is the process running?"""
    return jsonify({"status": "healthy"}), 200

@health_app.route('/ready')
def ready():
    """Readiness probe - can it handle traffic?"""
    # Check Slack connection, LiteLLM availability, etc.
    try:
        # Add checks here
        return jsonify({"status": "ready"}), 200
    except Exception as e:
        return jsonify({"status": "not ready", "error": str(e)}), 503

# Run health app in separate thread
import threading
threading.Thread(
    target=lambda: health_app.run(host='0.0.0.0', port=8080),
    daemon=True
).start()
```

---

## Security Hardening

### 1. Secrets Management

**DO NOT:**
- ❌ Commit secrets to Git
- ❌ Use `.env` in production
- ❌ Hardcode API keys

**DO:**
- ✅ Use Kubernetes Secrets (or Vault)
- ✅ Rotate secrets regularly
- ✅ Use least-privilege principles

**Setup with Kubernetes:**

```bash
# Create secrets from file
kubectl create secret generic ledger-bot-secrets \
  --from-literal=slack-bot-token=$SLACK_BOT_TOKEN \
  --from-literal=slack-app-token=$SLACK_APP_TOKEN \
  --from-literal=litellm-key=$LITELLM_DEVELOPER_KEY \
  -n bor-write
```

Or use **sealed-secrets** or **HashiCorp Vault** (preferred at enterprise scale).

### 2. Rate Limiting

Add to prevent abuse:

```python
from functools import wraps
from collections import defaultdict
import time

# Simple in-memory rate limiter
user_requests = defaultdict(list)
RATE_LIMIT = 10  # requests per minute

def rate_limit(func):
    @wraps(func)
    def wrapper(event, say, client):
        user_id = event.get("user")
        now = time.time()

        # Clean old requests
        user_requests[user_id] = [
            t for t in user_requests[user_id]
            if now - t < 60
        ]

        # Check limit
        if len(user_requests[user_id]) >= RATE_LIMIT:
            say("Rate limit exceeded. Please wait a moment before asking again.")
            return

        user_requests[user_id].append(now)
        return func(event, say, client)

    return wrapper

@rate_limit
@slack_app.event("app_mention")
def handle_mention(event, say, client):
    # ... existing code
```

### 3. Input Validation

Add validation for user inputs:

```python
def sanitize_question(question: str) -> str:
    """Sanitize user input"""
    # Remove excessive whitespace
    question = " ".join(question.split())

    # Limit length
    if len(question) > 1000:
        raise ValueError("Question too long (max 1000 chars)")

    # Basic injection prevention
    if any(char in question for char in [';', '`', '\x00']):
        raise ValueError("Invalid characters in question")

    return question
```

### 4. Dependencies

```bash
# Keep dependencies updated
pip install pip-audit
pip-audit

# Or use Dependabot in GitHub
```

---

## Monitoring & Observability

### 1. Logging

Add structured logging:

```python
import logging
import json

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

def log_event(event_type: str, **kwargs):
    """Structured logging"""
    log_entry = {
        "timestamp": time.time(),
        "event": event_type,
        **kwargs
    }
    logger.info(json.dumps(log_entry))

# Usage
log_event("question_received", user=user_id, question_length=len(question))
log_event("llm_call_started", model="claude-sonnet-4.5")
log_event("response_sent", response_length=len(answer), duration=elapsed)
```

### 2. Metrics

Add Prometheus metrics:

```python
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
questions_total = Counter('ledger_bot_questions_total', 'Total questions asked')
response_time = Histogram('ledger_bot_response_time_seconds', 'Response time')
errors_total = Counter('ledger_bot_errors_total', 'Total errors', ['error_type'])

# Start metrics server
start_http_server(9090)

# Use in code
questions_total.inc()
with response_time.time():
    # Process question
    pass
```

### 3. Alerts

Setup alerts for:

```yaml
# alerts.yaml
groups:
- name: ledger-bot
  rules:
  - alert: HighErrorRate
    expr: rate(ledger_bot_errors_total[5m]) > 0.1
    for: 5m
    annotations:
      summary: "High error rate in Ledger Bot"

  - alert: SlowResponses
    expr: ledger_bot_response_time_seconds{quantile="0.95"} > 10
    for: 5m
    annotations:
      summary: "95th percentile response time > 10s"

  - alert: LedgerBotDown
    expr: up{job="ledger-bot"} == 0
    for: 1m
    annotations:
      summary: "Ledger Bot is down"
```

### 4. Dashboards

Create Grafana dashboard tracking:
- Questions per hour
- Response times (p50, p95, p99)
- Error rates
- Active users
- LiteLLM API costs

---

## CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy Ledger Bot

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest tests/ --cov
    - name: Lint
      run: |
        pip install black flake8
        black --check .
        flake8 .

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build Docker image
      run: docker build -t gcr.io/wealthsimple/ledger-bot:${{ github.sha }} .
    - name: Push to registry
      run: |
        echo ${{ secrets.GCR_KEY }} | docker login -u _json_key --password-stdin gcr.io
        docker push gcr.io/wealthsimple/ledger-bot:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/ledger-bot \
          ledger-bot=gcr.io/wealthsimple/ledger-bot:${{ github.sha }} \
          -n bor-write
        kubectl rollout status deployment/ledger-bot -n bor-write
```

---

## Testing Strategy

### 1. Unit Tests

```python
# tests/test_handlers.py
import pytest
from app import handle_question

def test_handle_question_basic():
    question = "What is GL Publisher?"
    answer = handle_question(question)
    assert len(answer) > 0
    assert "GL Publisher" in answer

def test_rate_limiting():
    # Test rate limit enforcement
    pass

def test_input_validation():
    with pytest.raises(ValueError):
        sanitize_question("x" * 2000)  # Too long
```

### 2. Integration Tests

```python
# tests/test_integration.py
import pytest
from slack_sdk.errors import SlackApiError

def test_slack_connection():
    """Test that bot can connect to Slack"""
    # Test with real Slack token (in CI)
    pass

def test_litellm_connection():
    """Test that bot can call LiteLLM"""
    # Test with real LiteLLM endpoint
    pass
```

### 3. Load Testing

```python
# tests/load_test.py
import locust

class LedgerBotUser(locust.HttpUser):
    @locust.task
    def ask_question(self):
        # Simulate user asking question
        pass

# Run: locust -f tests/load_test.py
```

---

## Support & On-Call

### 1. Runbook

Create `/Users/kayla.lu/ledger-bot-app/docs/RUNBOOK.md`:

**Common Issues:**

| Issue | Symptoms | Solution |
|-------|----------|----------|
| Bot not responding | No replies in Slack | Check k8s pods, logs |
| Slow responses | >10s response time | Check LiteLLM status, increase replicas |
| High error rate | Errors in logs | Check API keys, LiteLLM quota |
| Out of memory | Pod restarts | Increase memory limits |

**Monitoring:**
- Dashboard: https://grafana.company.com/ledger-bot
- Logs: `kubectl logs -f deployment/ledger-bot -n bor-write`
- Alerts: PagerDuty integration

### 2. On-Call Setup

**PagerDuty Integration:**
```yaml
# Add to alerts.yaml
annotations:
  pagerduty: "bor-write-oncall"
```

**Escalation:**
1. Primary: BOR Write on-call
2. Secondary: Kayla (owner)
3. Tertiary: Engineering Manager

### 3. SLA / SLO

Define service levels:
- **Availability:** 99.5% uptime (3.6 hours downtime/month)
- **Response Time:** 95th percentile < 5 seconds
- **Error Rate:** < 1% of requests

---

## Rollout Plan

### Phase 1: Internal Beta (Week 1-2)
- **Audience:** BOR Write team only (~10 people)
- **Goal:** Find bugs, gather feedback
- **Deployment:** Production k8s, but not announced widely
- **Success Criteria:**
  - Bot responds to >95% of questions
  - No critical bugs
  - Positive feedback from team

### Phase 2: Limited Release (Week 3-4)
- **Audience:** Teams that frequently integrate with GL Publisher
  - Example: Cash team, Trade team, Crypto team
- **Goal:** Validate with real users, tune knowledge base
- **Deployment:** Production, announced in specific channels
- **Success Criteria:**
  - 50+ questions answered
  - <5% error rate
  - Knowledge gaps identified and filled

### Phase 3: General Availability (Week 5+)
- **Audience:** All engineering
- **Goal:** Widespread adoption
- **Deployment:** Production, announced company-wide
- **Success Criteria:**
  - 100+ questions/week
  - Positive NPS score
  - Reduced support load on BOR Write

### Rollback Plan

If issues arise:
```bash
# Rollback to previous version
kubectl rollout undo deployment/ledger-bot -n bor-write

# Or disable bot
kubectl scale deployment/ledger-bot --replicas=0 -n bor-write
```

---

## Cost Estimation

### Infrastructure
- **Kubernetes:** ~$50/month (2 small pods)
- **Monitoring:** Included in company infrastructure
- **CI/CD:** Included in GitHub Actions

### API Costs
- **LiteLLM:** ~$0.02 per question (Claude Sonnet 4.5)
- **Estimated usage:**
  - Beta: 50 questions/week = $1/week = $4/month
  - Limited: 200 questions/week = $16/month
  - GA: 500 questions/week = $40/month

**Total estimated cost:** ~$100-150/month at full adoption

### Cost Optimization Options
1. Use Haiku for simple questions (10x cheaper)
2. Cache common responses
3. Rate limit per user
4. Implement prompt caching (Phase 2)

---

## Production Readiness Checklist

### Code
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Linting/formatting applied
- [ ] Type hints added
- [ ] Error handling comprehensive

### Infrastructure
- [ ] Dockerfile created
- [ ] Kubernetes manifests written
- [ ] Health checks implemented
- [ ] Resource limits defined
- [ ] Secrets in secret manager

### Observability
- [ ] Structured logging added
- [ ] Metrics exposed
- [ ] Dashboards created
- [ ] Alerts configured
- [ ] Log aggregation setup

### Documentation
- [ ] README updated
- [ ] Runbook written
- [ ] Architecture documented
- [ ] API docs complete
- [ ] Incident response plan

### Security
- [ ] Security review completed
- [ ] Dependencies scanned
- [ ] Rate limiting implemented
- [ ] Input validation added
- [ ] Secrets rotated

### Process
- [ ] CI/CD pipeline working
- [ ] Load testing completed
- [ ] Rollout plan approved
- [ ] On-call rotation defined
- [ ] Success metrics defined

---

## Next Steps

1. **This week:** Add tests, create Dockerfile
2. **Next week:** Set up k8s manifests, deploy to staging
3. **Week 3:** Internal beta with BOR Write team
4. **Week 4:** Limited release to key teams
5. **Week 5+:** General availability

---

## Questions for Platform/DevOps Team

Before deploying, clarify:

1. **Kubernetes access:** Do we have a namespace? Who approves?
2. **Secrets management:** Vault vs Sealed Secrets vs k8s Secrets?
3. **CI/CD:** Use company standard pipeline or custom?
4. **Monitoring:** Which tools (Prometheus/Grafana/Datadog)?
5. **Cost approval:** Who approves LiteLLM API spend?
6. **On-call:** Integrate with existing rotation or new?

---

## Resources

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/)
- [12-Factor App](https://12factor.net/)
- [Slack App Security](https://api.slack.com/authentication/best-practices)
- [Production Readiness Checklist](https://gruntwork.io/devops-checklist/)

---

*Remember: Production is a journey, not a destination. Start simple, iterate based on real usage.*
