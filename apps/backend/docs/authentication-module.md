# Authentication Module Scaffolding

This document describes the structure and implementation blueprint of the `auth` module.

## Module Layout

The `src/modules/auth` folder is organized as follows:

```text
src/modules/auth/
├── application/
│   └── usecases/
│       └── login_usecase.py       # Login execution coordinator (scaffolded)
├── domain/
│   ├── entities/
│   │   └── user.py                # User and Session entities (TODO)
│   ├── repositories/
│   │   └── user_repository.py     # Repository port interface
│   └── services/
│       └── auth_service.py        # Core auth business rules
├── infrastructure/
│   ├── models/
│   │   └── user_model.py          # SQLAlchemy user mappings
│   ├── repositories/
│   │   └── user_repository_impl.py # SQLAlchemy repository adapter
│   └── uow/
│       └── auth_uow.py            # Unit of Work transaction scope
├── presentation/
│   ├── routers/
│   │   └── auth_routers_registry.py # FastAPI controllers for auth
│   └── schemas/
│       └── auth_schemas.py        # Pydantic validation schemas
└── auth_container.py              # Dependency-injector DI wiring
```

---

## Blueprints for Future Features

### 1. User Registration Flow
1. Receive request via POST `/api/v1/auth/register` with `RegisterRequestSchema`.
2. Controller invokes `RegisterUserUseCase` (to be created).
3. Usecase verifies email uniqueness using `IUserRepository`.
4. Usecase triggers password hashing using `HasherService`.
5. Usecase instantiates domain `UserEntity`, saves it through repository, and emits `UserCreatedEvent`.
6. Session is committed by the `AuthUOW`.

### 2. Login Flow
1. Receive request via POST `/api/v1/auth/login`.
2. `LoginUseCase` fetches the user model via `IUserRepository`.
3. Verifies hash using Argon2.
4. Generates session UUID and saves session using `UserSessionDomainService`.
5. Sets `session_uuid` as a secure HttpOnly cookie on response.

### 3. Middleware Integration
Once session tables and repositories are created, update `AuthMiddleware` to query the `GetUserSessionUseCase` to validate the incoming session cookie.
