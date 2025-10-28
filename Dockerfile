# Firecrawl Dashboard Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY MANIFEST.in .
COPY README.md .
COPY src/ ./src/
COPY run_dashboard.py .
COPY firecrawl-dashboard .

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install Python dependencies using full path to uv
RUN /root/.local/bin/uv pip install --system -e .

# Expose dashboard port
EXPOSE 8000

# Set environment variables with defaults
ENV DASHBOARD_HOST=0.0.0.0
ENV DASHBOARD_PORT=8000
ENV FIRECRAWL_API_URL=http://api:3002
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_DB=0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the dashboard
CMD ["python", "run_dashboard.py"]
