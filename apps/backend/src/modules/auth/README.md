# Authentication Module Scaffolding

This module implements the **Domain-Driven Design (DDD)** and **Clean Architecture** patterns, mirroring the structural separation of the rest of the backend codebase.

## Directory Structure

```text
src/modules/auth/
├── application/
│   ├── usecases/      # Use cases orchestrating domain workflow
│   ├── listeners/     # Event handlers reacting to domain events
│   └── tasks/         # Async background workers
├── domain/
│   ├── entities/      # Pure business objects and entities
│   ├── repositories/  # Repository interfaces (ports)
│   ├── services/      # Domain services
│   └── events/        # Immutable domain events
├── infrastructure/
│   ├── models/        # SQLAlchemy ORM models
│   ├── repositories/  # Repository implementations (adapters)
│   └── uow/           # Unit of Work implementations
├── presentation/
│   ├── routers/       # FastAPI endpoints
│   └── schemas/       # Pydantic schemas (DTOs)
└── auth_container.py  # Dependency Injection setup
```

## TODO Checklist for Future Authentication Implementation
- [ ] Define SQLAlchemy database model under `infrastructure/models/user_model.py`.
- [ ] Design pure business entities `UserEntity` and `SessionEntity` in `domain/entities/`.
- [ ] Implement query logic in `infrastructure/repositories/user_repository_impl.py`.
- [ ] Wire user creation and password hashing (using Argon2) in `application/usecases/`.
- [ ] Wire dependencies inside `auth_container.py` declarative container.
- [ ] Implement JWT/Cookie session setup, and update `AuthMiddleware` for session check validation.
- [ ] Configure Alembic migrations for users and sessions.
