FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for psycopg2 and build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
# Copy uv.lock if available, otherwise fallback
COPY uv.lock* .

RUN pip install uv
RUN uv pip install --system -r pyproject.toml

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
