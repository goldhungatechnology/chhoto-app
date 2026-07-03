# Chhoto App Backend

Chhoto App Backend is a production-grade FastAPI boilerplate structured around **Domain-Driven Design (DDD)** and **Clean Architecture** patterns, leveraging modular bounded contexts, declarative dependency injection, and automatic database migrations.

---

## Architecture Overview
The project divides concerns into distinct, strict layers. The domain model resides at the center and is completely isolated from transport protocols (FastAPI) and persistence engines (SQLAlchemy).

For a detailed review of our architecture and standards, consult the documentation:
* [Architecture Guide](docs/architecture.md)
* [Coding Conventions and Naming Standards](docs/coding-standards.md)
* [Authentication Module Blueprint](docs/authentication-module.md)

---

## Directory Structure
```text
├── .agents/                 # AI Development Environment
│   └── skills/              # Flat skill files guiding AI coding agents
├── docker/                  # Docker Compose configuration profiles
├── docs/                    # Technical documentation
├── env/                     # Environment configuration profiles (.env.local, .env.development, etc.)
├── migrations/              # Alembic database migrations and custom imperatively-modeled migration base
├── src/
│   ├── core/                # Core configurations, lifespans, and response schema utilities
│   ├── modules/             # Bounded contexts / feature domains
│   │   └── auth/            # Authentication context skeleton (DDD layed)
│   └── shared/              # Shared kernel utilities, middlewares, exceptions, and DB routers registry
└── tests/                   # Pytest testing suite
```

---

## Local Development Quickstart

### Prerequisites
Ensure you have the following installed on your machine:
- **Python**: version `3.13`
- **uv**: package manager
- **Docker / Docker Compose**: for local services (Postgres, Redis)

### Step 1: Initial Project Setup
Install dependencies and configure pre-commit hooks:
```bash
make setup
```

### Step 2: Configure Environment Variables
Activate the local environment configuration profile:
```bash
cp env/.env.local env/.env
```

### Step 3: Run Database & Cache Containers
Spin up local Postgres and Redis instances:
```bash
make localup
```

### Step 4: Database Migrations
Apply alembic schema updates to your database:
```bash
make migrate
```

### Step 5: Start the API Server
Start the development server with live reload:
```bash
make run
```
The health check endpoint is available at `http://localhost:8080/health`.

---

## Running the Tests
To run the automated pytest test suite (it launches and destroys an isolated Postgres container dynamically):
```bash
make test
```

---

## Code Quality Utilities
Adhere to code review standards by running formatting and linting:
```bash
# Run Ruff linting check and fix
make lint

# Run Ruff formatting
make format

# Verify type annotations
make typecheck
```
