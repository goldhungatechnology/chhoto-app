FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY apps/backend/pyproject.toml .
COPY apps/backend/uv.lock .

COPY apps/backend/ .
COPY apps/packages/chhoto_encoding/ ../packages/chhoto_encoding/


RUN uv sync --locked
EXPOSE 8000

CMD ["uv","run","uvicorn","src.main:create_app","--host","0.0.0.0","--port","8000","--factory"]
