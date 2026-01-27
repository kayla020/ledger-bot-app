# Production Dockerfile for Ledger Bot
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY knowledge_base.txt .

# Create non-root user for security
RUN useradd -m -u 1000 ledgerbot && \
    chown -R ledgerbot:ledgerbot /app

# Switch to non-root user
USER ledgerbot

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Expose health check port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
