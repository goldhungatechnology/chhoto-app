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

COPY pyproject.toml .
COPY uv.lock .

COPY . .


RUN uv sync --locked --system
EXPOSE 8000

CMD ["uvicorn","src.main:create_app","--host","0.0.0.0","--port","8000","--factory"]
