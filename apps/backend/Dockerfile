FROM python:3.13-slim as BUILDER

WORKDIR /usr/local/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

COPY apps/backend/pyproject.toml .
COPY apps/backend/uv.lock .
COPY apps/packages/chhoto_encoding ../packages/chhoto_encoding

COPY apps/backend .

RUN uv sync --locked

FROM python:3.13-slim as RUNTIME

WORKDIR /app

# Install PostgreSQL runtime library and curl (used by the healthcheck)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*


COPY --from=BUILDER /usr/local/app /app
COPY --from=BUILDER /usr/local/packages /packages
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

CMD ["uvicorn","src.main:app","--host","0.0.0.0","--port","8000"]
