# syntax=docker/dockerfile:1

# ==============================================================================
# Stage 1: Build dependencies
# ==============================================================================
FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.1.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="${POETRY_HOME}/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files and LICENSE
COPY pyproject.toml poetry.lock LICENSE ./

# Install dependencies
RUN poetry install --without dev --no-directory --compile

# ==============================================================================
# Stage 2: Runtime
# ==============================================================================
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:/usr/local/bin:$PATH" \
    TMPDIR="/tmp/app"

# Create non-root user and temp directory
RUN useradd -m -u 1000 appuser \
    && mkdir -p /home/appuser/.local/bin \
    && mkdir -p /tmp/app \
    && chown -R appuser:appuser /home/appuser \
    && chown -R appuser:appuser /tmp/app

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgomp1 \
        curl \
        libfreetype6 \
        libpng16-16 \
        libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0"]
