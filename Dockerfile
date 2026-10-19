# AutoCoach Production Dockerfile for Self-Hosted Deployment
# Multi-stage build with UV and Python 3.13 on Debian Bookworm Slim

ARG PYTHON_VERSION=3.13
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS base

ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1

# --- Build Stage ---
FROM base AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications and project readme to leverage Docker layer caching
COPY pyproject.toml uv.lock README.md ./

# Install dependencies deterministically (without installing the project itself yet)
RUN uv sync --locked --no-install-project

# Copy remaining source files
COPY . .

# Install the project and pre-compile bytecode
RUN uv sync --locked && uv run python -c "import autocoach"

# --- Production Stage ---
FROM base

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

WORKDIR /app

# Copy built application and virtual environment with correct ownership
COPY --from=build --chown=appuser:appuser /app /app

# Health check probe on port 8085
EXPOSE 8085

# Switch to non-root user
USER appuser

# Start the LiveKit agent worker in production mode
CMD ["uv", "run", "python", "-m", "autocoach.agent", "start"]
