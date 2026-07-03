# Development Guide

This guide details the procedures for setting up and working on the Chhoto App backend locally.

## Prerequisite Tools
- **Python**: version `3.13`
- **uv**: Python package installer and virtualenv manager
- **Docker & Docker Compose**: For running PostgreSQL/Redis

---

## Local Installation

1. **Clone the repository** and navigate to the backend directory:
   ```bash
   cd apps/backend
   ```

2. **Initialize Environment and Install Dependencies**:
   ```bash
   # Sets up virtualenv and installs dependencies
   make setup
   ```

3. **Configure Environment Variables**:
   Copy the local environment config to activate your local configuration profile:
   ```bash
   cp env/.env.local env/.env
   ```

---

## Running Infrastructure Services

Start the development database and Redis cache locally using Docker Compose:
```bash
make localup
```

Stop the services:
```bash
make localdown
# Or to clear all persistent volumes:
make localdownv
```

---

## Database Migrations (Alembic)

To generate a new database migration:
```bash
make migration name=create_users_table msg="create users table"
```

To apply all migrations to the local database:
```bash
make migrate
```

To rollback the last migration:
```bash
make downgrade
```

---

## Running the Application

Start the FastAPI application in development mode (with hot reloading enabled on localhost:8080):
```bash
make run
```

---

## Code Quality Checkers

Run these utilities before committing code changes to verify formatting and type correctness:
```bash
# Run linting checks (Ruff)
make lint

# Run code format (Ruff)
make format

# Run Pyright static type checker
make typecheck
```

---

## Running the Test Suite

Running tests automatically creates a temporary database container (`chhoto_db_test`), applies all migrations, runs the tests, and tears the container down:
```bash
make test
```
