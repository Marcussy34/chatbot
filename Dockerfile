# Multi-stage build for Google Cloud Run
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app
RUN mkdir -p /app/.cache/huggingface

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy and run model preload script
COPY preload_models.py .
RUN python preload_models.py

# Stage 2: Production image
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8080 \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create app directory and set permissions
WORKDIR /app
RUN mkdir -p /app/.cache/huggingface && \
    chown -R appuser:appuser /app

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy pre-downloaded models from builder stage
COPY --from=builder /app/.cache /app/.cache

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser chatbot/ ./chatbot/
COPY --chown=appuser:appuser data/ ./data/
COPY --chown=appuser:appuser scripts/ ./scripts/

# Copy entry point script
COPY --chown=appuser:appuser requirements.txt .
# Startup handled directly with uvicorn

# Switch to non-root user
USER appuser

# Expose port (Cloud Run will override this)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Start the application with optimizations for Cloud Run
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT 