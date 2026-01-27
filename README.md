# Ledger Bot 🤖

An AI-powered Slack bot that helps teams understand and integrate with the GL Publisher and ledger system.

## Overview

Ledger Bot is a comprehensive knowledge assistant built with Claude Sonnet 4.5 that provides:
- **Team onboarding** - Help new engineers understand GL Publisher
- **Troubleshooting** - Debug activity issues, schema problems, etc.
- **Documentation** - On-demand access to ADRs, schemas, and patterns
- **Best practices** - Guide teams on proper integration patterns

Built during an exploration day, this project demonstrates rapid prototyping with Claude Code and production-ready deployment practices.

## Architecture

```
┌─────────────────┐
│  Slack Bot      │
│  (Socket Mode)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LiteLLM        │
│  Gateway        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Claude         │
│  Sonnet 4.5     │
└─────────────────┘
```

**Key Features:**
- Socket Mode (no webhooks, no ngrok)
- Company LiteLLM infrastructure
- Health check endpoints for Kubernetes
- Comprehensive knowledge base (6.5KB)
- Fast response times with "Thinking..." indicator

## Quick Start

### Local Development

```bash
# 1. Clone repository
git clone <repo-url>
cd ledger-bot-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your tokens:
# - SLACK_BOT_TOKEN
# - SLACK_APP_TOKEN
# - LITELLM_DEVELOPER_KEY

# 4. Run locally
python app.py
```

### Usage

**In Slack:**
- Direct message: `What is GL Publisher?`
- Mention in channel: `@ledgerbot How do I create ledger lines?`
- Get help: `@ledgerbot What's an Impact Builder?`

## Production Deployment

### Prerequisites
- Kubernetes cluster access
- Docker registry access
- Secret management (Kubernetes Secrets or Vault)

### Deploy to Kubernetes

```bash
# 1. Build and push Docker image
docker build -t <registry>/ledger-bot:latest .
docker push <registry>/ledger-bot:latest

# 2. Create secrets
kubectl create secret generic ledger-bot-secrets \
  --from-literal=slack-bot-token=xoxb-... \
  --from-literal=slack-app-token=xapp-... \
  --from-literal=litellm-developer-key=sk-... \
  -n bor-write

# 3. Deploy
kubectl apply -f k8s/

# 4. Verify deployment
kubectl get pods -n bor-write -l app=ledger-bot
kubectl logs -n bor-write -l app=ledger-bot --tail=50
```

### Health Checks

- **Liveness**: `GET /health` - Returns 200 if app is alive
- **Readiness**: `GET /ready` - Returns 200 if ready to serve, 503 if not

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_app.py::TestHealthEndpoints::test_health_endpoint
```

## CI/CD

GitHub Actions workflow automatically:
- Runs tests on all PRs
- Performs security scanning
- Builds Docker images on main branch
- (TODO) Deploys to Kubernetes

See `.github/workflows/ci.yaml` for details.

## Project Structure

```
ledger-bot-app/
├── app.py                  # Main Slack bot application
├── knowledge_base.txt      # Curated GL Publisher knowledge
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container image definition
├── pytest.ini              # Test configuration
├── run_tests.sh           # Test runner script
├── .github/
│   └── workflows/
│       └── ci.yaml         # CI/CD pipeline
├── k8s/                    # Kubernetes manifests
│   ├── deployment.yaml     # Bot deployment
│   ├── service.yaml        # Service definition
│   └── secret.yaml.template # Secret template
├── tests/                  # Unit tests
│   ├── test_app.py
│   └── README.md
├── docs/                   # Documentation
│   ├── EXPLORATION_DAY_SUMMARY.md
│   ├── DEMO_SCRIPT.md
│   ├── LESSONS_LEARNED.md
│   ├── PRODUCTION_DEPLOYMENT.md
│   └── plans/
└── mcp-server/            # MCP server (separate interface)
```

## Documentation

- **[Exploration Day Summary](docs/EXPLORATION_DAY_SUMMARY.md)** - What was built and why
- **[Demo Script](docs/DEMO_SCRIPT.md)** - 15-minute presentation guide
- **[Lessons Learned](docs/LESSONS_LEARNED.md)** - Insights and retrospective
- **[Production Deployment](docs/PRODUCTION_DEPLOYMENT.md)** - Comprehensive deployment guide
- **[MCP Server Guide](mcp-server/TEAM_INSTALL_GUIDE.md)** - Personal Claude Desktop integration

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SLACK_BOT_TOKEN` | Bot user OAuth token (xoxb-...) | Yes |
| `SLACK_APP_TOKEN` | App-level token (xapp-...) | Yes |
| `LITELLM_DEVELOPER_KEY` | LiteLLM API key | Yes |
| `HEALTH_PORT` | Health check server port | No (default: 8080) |

### Kubernetes Resources

- **CPU**: 250m request, 500m limit
- **Memory**: 256Mi request, 512Mi limit
- **Replicas**: 1 (Socket Mode = single instance)

## Cost Estimation

- **Infrastructure**: ~$20-30/month (Kubernetes resources)
- **API calls**: ~$0.01-0.05 per question
- **Estimated total**: $100-150/month for moderate usage

## Monitoring

The bot exposes metrics for:
- Question count
- Response latency
- Error rates
- LLM token usage

Configure Prometheus scraping on port 8080, path `/metrics`.

## Support

- **Questions**: Ask in #bor-write-eng
- **Issues**: Create GitHub issue
- **Maintainer**: Kayla (@kayla.lu)

## Roadmap

### Phase 1 (Current)
- ✅ Slack bot with static knowledge
- ✅ Health checks and monitoring
- ✅ Production deployment manifests
- ✅ Basic test coverage
- 🏗️ MCP server implementation

### Phase 2 (Next Sprint)
- GraphQL API integration (live activity status)
- Database access (ledger state queries)
- Kafka monitoring (topic inspection)
- Enhanced testing (integration, load tests)

### Phase 3 (Future)
- Tool calling for dynamic knowledge retrieval
- RAG system for full repository search
- Multi-team customization
- Analytics dashboard

## License

Internal Wealthsimple project - not for external distribution.

## Acknowledgments

Built with:
- [Slack Bolt for Python](https://slack.dev/bolt-python/)
- [Claude Sonnet 4.5](https://www.anthropic.com/claude)
- [LiteLLM](https://docs.litellm.ai/)
- [Claude Code](https://claude.ai/claude-code)

Special thanks to the BOR Write team for domain expertise and the Platform team for LiteLLM infrastructure.
