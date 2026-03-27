FROM python:3.13-slim

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first (better Docker cache)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Run migrations and start server
CMD uv run alembic upgrade head && uv run uvicorn app.api.app:create_app --factory --host 0.0.0.0 --port ${PORT:-8000}
