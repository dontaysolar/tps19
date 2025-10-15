# TPS19 Crypto Trading System
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 tps19 && \
    mkdir -p /app /app/data /app/logs /app/models && \
    chown -R tps19:tps19 /app

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY --chown=tps19:tps19 requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy application code
COPY --chown=tps19:tps19 . .

# Switch to non-root user
USER tps19

# Create necessary directories
RUN mkdir -p data logs models

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose ports
EXPOSE 8000

# Default command
CMD ["python", "main.py", "start"]