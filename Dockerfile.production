# =====================================================
# AI Visibility Platform - Production Docker Image
# =====================================================

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install OS dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Copy entire project
COPY . .

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install application
RUN pip install --no-cache-dir -e ".[dev]"

# Make startup script executable
RUN chmod +x start.sh

# Create non-root user
RUN groupadd -r app && \
    useradd -r -g app app

RUN chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s \
             --timeout=10s \
             --start-period=20s \
             --retries=3 \
CMD curl -f http://localhost:8000/health || exit 1

CMD ["/bin/bash", "/app/start.sh"]
