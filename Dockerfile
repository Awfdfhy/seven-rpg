# Seven RPG — Dockerfile (Python placeholder)
# Directive: Do not introduce a framework or dependency without recording
# its purpose, maintenance risk, license, size, and alternatives.
# Finalize after ADR-0001 stack selection.

FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run tests as part of build
RUN pytest tests/ -v

# Runtime stage
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install only runtime dependencies
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash sevenrpg && \
    chown -R sevenrpg:sevenrpg /app
USER sevenrpg

# Expose port (if API is used)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "main.py"]