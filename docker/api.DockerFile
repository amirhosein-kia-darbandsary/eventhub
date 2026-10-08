# syntax=docker/dockerfile:1

############################
# Builder
############################
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Dependency files first -> Docker cache
COPY pyproject.toml uv.lock ./

# Create production virtualenv
RUN uv sync \
    --frozen \
    --no-dev \
    --no-install-project

# Now application source
COPY app/ ./app/

# Install project itself
RUN uv sync \
    --frozen \
    --no-dev


############################
# Runtime
############################
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Create non-root user
RUN groupadd --system app \
    && useradd --system \
        --gid app \
        --create-home \
        --home-dir /home/app \
        app

# Copy only what runtime needs
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/app /app/app

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]