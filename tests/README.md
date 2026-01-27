# Ledger Bot Tests

## Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_app.py

# Run specific test
pytest tests/test_app.py::TestHealthEndpoints::test_health_endpoint
```

## Test Structure

- `test_app.py` - Unit tests for main application logic
  - Health check endpoints
  - Knowledge base loading
  - Configuration validation

## Adding New Tests

1. Create test file in `tests/` directory with `test_` prefix
2. Use pytest fixtures for common setup
3. Mock external dependencies (Slack, LiteLLM)
4. Run tests before committing

## Test Coverage

Current coverage areas:
- ✅ Health check endpoints (`/health`, `/ready`)
- ✅ Knowledge base loading
- ✅ Environment configuration
- ⏭️ Slack event handlers (requires mocking)
- ⏭️ LLM integration (requires mocking)
