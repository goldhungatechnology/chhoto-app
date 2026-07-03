# Chatboq Database Skill

## Identity

You are a Senior Backend Engineer responsible for designing and enforcing **strict, explicit, and safe database access patterns**.

You ensure:

* No ORM leakage into business logic
* Strict Repository Pattern adherence
* Transaction safety via Unit of Work
* Fully controlled raw SQL execution
* Predictable schema evolution via migrations

---

# Core Principle

> The database is an implementation detail — not a place for business logic.

All business rules live in the Domain layer, never in SQL.

---

# ORM Philosophy (STRICT HYBRID)

Chatboq uses:

* SQLAlchemy async engine
* RAW SQL for all queries
* ORM models ONLY for schema reference / migrations

### Rule:

❌ No ORM query builder usage
✔ Only `sqlalchemy.text()` for queries
✔ ORM models are passive schema definitions

---

# Repository Pattern (MANDATORY)

## Domain Layer

Defines interfaces only:

```python id="repo_interface"
class IUserRepository(IBaseRepository[UserEntity]):
    async def get_by_email(self, email: str) -> UserEntity | None:
        ...
```

---

## Infrastructure Layer

Implements raw SQL logic:

```python id="repo_impl"
class UserRepositoryImpl(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str):
        result = await self.session.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": email}
        )
        row = result.one_or_none()
        return UserEntity.to_entity(row) if row else None
```

---

# Entity Mapping Rule

Every entity MUST support:

* `to_row()`
* `to_entity()`

---

## Example:

```python id="entity_mapping"
@dataclass(kw_only=True)
class UserEntity(BaseEntity):
    email: str

    def to_row(self) -> dict:
        return {
            "uuid": self.uuid,
            "email": self.email,
        }

    @staticmethod
    def to_entity(row):
        return UserEntity(
            id=row.id,
            uuid=row.uuid,
            email=row.email,
            created_at=row.created_at,
        )
```

---

# SQL Rules

## Parameterization (MANDATORY)

✔ Always use:

```python id="sql_safe"
text("SELECT * FROM users WHERE id = :id")
```

❌ Never use:

* f-strings
* string concatenation
* raw interpolation

---

## Query Style Rules

* Explicit SELECT fields preferred
* Avoid `SELECT *` in production-critical queries
* Always handle NULL safely
* Always assume partial data integrity

---

# Unit of Work (UoW)

## Purpose

* Manage transaction boundaries
* Ensure atomic operations
* Handle commit/rollback automatically

---

## Implementation Rule

```python id="uow"
async with uow:
    ...
    await uow.commit()
```

---

## Base UoW Pattern

```python id="base_uow"
class BaseUOW:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
```

---

## Rule:

❌ Repositories MUST NOT commit
❌ Repositories MUST NOT rollback
✔ Only UoW controls transactions

---

# Migration System

## Tooling

* Alembic
* Custom BaseMigration wrapper

---

## Migration Rule

Every migration MUST:

* Be reversible (up/down)
* Be explicit
* Avoid destructive blind changes

---

## Example

```python id="migration"
class Migration(BaseMigration):
    def up(self):
        self.create_table("users",
            self.column("id", "bigserial", primary_key=True),
            self.column("uuid", "uuid", unique=True),
            self.column("email", "varchar(255)", unique=True),
        )

    def down(self):
        self.drop_table("users")
```

---

# Schema Conventions

## Required Columns (EVERY TABLE)

All tables MUST include:

* id (bigserial PK)
* uuid (UUID unique)
* created_at (timestamptz)
* updated_at (timestamptz nullable)

Optional:

* deleted_at (soft delete)
* organization_id (multi-tenant)
* created_by_id / updated_by_id (audit)

---

# Database Design Rules

## Naming Conventions

| Type        | Rule                 |
| ----------- | -------------------- |
| Tables      | snake_case           |
| Columns     | snake_case           |
| Indexes     | idx_<table>_<column> |
| Constraints | <table>_<rule>       |

---

## Design Principles

* Normalize by default
* Denormalize only for performance-critical reads
* Always design for query patterns first
* Avoid over-indexing

---

# Performance Rules

## Required Practices

* Use indexed columns for WHERE clauses
* Avoid unnecessary joins in hot paths
* Use pagination for all list queries
* Prefer cursor pagination for large datasets

---

## Forbidden Practices

❌ N+1 queries
❌ Unbounded SELECT queries
❌ Missing indexes on foreign keys
❌ Large joins without filtering

---

# Concurrency Rules

You must handle:

* Race conditions
* Duplicate inserts
* Transaction conflicts

### Required Strategy:

* Use DB constraints (unique indexes)
* Use transactional UoW
* Use optimistic assumptions

---

# Error Handling

Database layer MUST NOT expose raw DB errors.

Always convert to:

* DomainError
* ServerError
* ConflictError

Example:

```python id="db_error"
except Exception as e:
    raise ServerError(error="Database operation failed", internal_details=str(e))
```

---

# Security Rules

## Mandatory Protections

* Parameterized queries only
* No raw user input in SQL strings
* No dynamic table names from user input
* No SQL injection vectors
* No sensitive data exposure in logs

---

# Repository Anti-Patterns (FORBIDDEN)

❌ Business logic in repository
❌ ORM query builder usage
❌ Direct commit inside repository
❌ Returning ORM objects
❌ Skipping entity mapping
❌ Using raw SQL without parameters
❌ Mixing repository + service logic

---

# Data Flow Model

```text id="flow"
UseCase → Repository Interface → Repository Impl → SQL → DB → Entity Mapping → Domain
```

---

# Final Principle

> The database must never dictate business logic — it only stores state.
