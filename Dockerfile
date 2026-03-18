# TaskForge Backend - Multi-stage build
# Targets: dev (default), prod

FROM python:3.11-slim AS base
WORKDIR /app

# System deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# --- Dev target: includes dev deps, for local docker compose ---
FROM base AS dev
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"
COPY . .
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --- Prod target: runtime deps only, smaller image ---
FROM base AS prod
COPY pyproject.toml .
COPY app/ app/
RUN pip install --no-cache-dir -e .
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
