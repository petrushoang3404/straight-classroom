FROM python:3.14-slim

# libgomp: onnxruntime's OpenMP runtime, missing from the slim image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# The code imports itself as `backend.xxx`, so the package lives at
# /app/backend and /app is the import root.
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/backend/.venv/bin:$PATH"
WORKDIR /app/backend

# Dependencies first, so code changes don't reinstall them.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Face model: the weights aren't committed. Fetched before the rest of the
# source is copied so editing code doesn't download them again. Settings
# requires the database vars to exist, but this step never connects.
COPY __init__.py config.py ./
COPY inference ./inference
RUN POSTGRES_USER=build POSTGRES_PASSWORD=build POSTGRES_DB=build \
    python -m backend.inference.fetch_weights

COPY . .

RUN useradd --system --no-create-home app
USER app

EXPOSE 8000

# Schema is managed by Alembic, so bring it up to date before serving.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --proxy-headers"]
