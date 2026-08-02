# chhoto-app

Chhoto is a URL shortener platform with analytics. A FastAPI backend, a Next.js
frontend, and Docker-based infrastructure.

## Repository layout

- `apps/backend` — FastAPI service (async SQLAlchemy, Redis, Dramatiq workers,
  Turnstile CAPTCHA, GeoIP lookups, Cloudinary/S3 uploads).
- `apps/frontend` — Next.js app (React 19, TanStack Query, pnpm).
- `apps/packages/chhoto_encoding` — shared slug-encoding package.
- `docker/` — docker-compose base/dev/staging/prod/test files.
- `infra/caddy/` — reverse-proxy config for the app/auth/api/go domains.
- `.github/workflows/ci-cd.yml` — CI checks for backend and frontend.

## Environment

Copy the backend env template and set values per environment:

```sh
cp apps/backend/env/.env.example apps/backend/env/.env.development
```

Prod requires a real `.env.production`; the app refuses to boot in production
with placeholder secrets.

## Local development

Backend (uses [uv](https://docs.astral.sh/uv/)):

```sh
cd apps/backend
uv sync --group dev
uv run uvicorn src.main:app --reload
```

Frontend:

```sh
cd apps/frontend
pnpm install
pnpm dev
```

## Docker

```sh
make devup     # start dev stack
make stagingup # start staging stack
```

## CI

`.github/workflows/ci-cd.yml` runs ruff (backend) and eslint, typecheck, and
build (frontend) on push/PR to `main` and `develop`.
