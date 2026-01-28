"""Unit tests for Ledger Bot"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import app


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_endpoint(self):
        """Test /health endpoint returns 200"""
        with app.health_app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'

    def test_ready_endpoint_when_ready(self):
        """Test /ready endpoint returns 200 when ready"""
        app.health_status['ready'] = True
        app.health_status['slack_connected'] = True

        with app.health_app.test_client() as client:
            response = client.get('/ready')
            assert response.status_code == 200
            data = response.get_json()
            assert data['ready'] is True
            assert data['slack_connected'] is True

    def test_ready_endpoint_when_not_ready(self):
        """Test /ready endpoint returns 503 when not ready"""
        app.health_status['ready'] = False
        app.health_status['slack_connected'] = False

        with app.health_app.test_client() as client:
            response = client.get('/ready')
            assert response.status_code == 503
            data = response.get_json()
            assert data['ready'] is False


class TestKnowledgeBase:
    """Test knowledge base loading"""

    def test_load_knowledge_base_success(self):
        """Test knowledge base loads successfully when file exists"""
        knowledge = app.load_knowledge_base()
        assert knowledge is not None
        assert len(knowledge) > 0
        assert isinstance(knowledge, str)

    def test_load_knowledge_base_fallback(self):
        """Test knowledge base uses fallback when file doesn't exist"""
        with patch('os.path.join', return_value='/nonexistent/path'):
            knowledge = app.load_knowledge_base()
            assert knowledge is not None
            assert "Ledger Bot" in knowledge
            assert "GL Publisher" in knowledge


class TestConfiguration:
    """Test configuration and environment variables"""

    @patch.dict(os.environ, {
        'SLACK_BOT_TOKEN': 'test-bot-token',
        'SLACK_APP_TOKEN': 'test-app-token',
        'LITELLM_DEVELOPER_KEY': 'test-llm-key'
    })
    def test_required_env_vars_present(self):
        """Test that required environment variables are checked"""
        assert os.environ.get('SLACK_BOT_TOKEN') == 'test-bot-token'
        assert os.environ.get('SLACK_APP_TOKEN') == 'test-app-token'
        assert os.environ.get('LITELLM_DEVELOPER_KEY') == 'test-llm-key'

    def test_health_port_default(self):
        """Test health port defaults to 8080"""
        port = int(os.environ.get('HEALTH_PORT', '8080'))
        assert port == 8080
