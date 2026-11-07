# Stage 1: Build virtual environment dependencies using uv
FROM python:3.14-slim AS builder

ARG ENV=development

# Install uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Tell uv to create the virtual environment at /venv (outside /app)
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/venv

WORKDIR /app

# Copy dependency configuration files
COPY pyproject.toml uv.lock* ./

# Synchronize dependencies into /venv directly from pyproject.toml
RUN uv sync --no-install-project --group ${ENV}

# Stage 2: Minimal runtime container
FROM python:3.14-slim AS runner

WORKDIR /app

ARG UID=1000
ARG GID=1000

# Create non-root user and prepare media, static, and logs directories with proper permissions
RUN groupadd -g "${GID}" appgroup && \
    useradd -u "${UID}" -g appgroup appuser && \
    mkdir -p /app/media /app/static /app/logs && \
    chown -R appuser:appgroup /app

# Environment configuration to activate virtual environment at /venv
ENV VIRTUAL_ENV=/venv \
    PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appgroup /venv /venv

# Copy application source code
COPY --chown=appuser:appgroup . .

# Expose default Django port
EXPOSE 8000

# Switch to non-root user for security
USER appuser

# Health-check routine via internal Django endpoint
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/').read()"]

# Default command to run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]