#!/bin/bash
# Test runner script for Ledger Bot

set -e

echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

echo "🧪 Running tests..."
pytest -v --tb=short

echo "✅ All tests passed!"
