# System Architecture

The Chhoto App Backend follows **Domain-Driven Design (DDD)** and **Clean Architecture** patterns.

## Architectural Philosophy
Our primary design goal is strict layer isolation: the core business domain should not depend on external frameworks, databases, or transport protocols.

```text
+-------------------------------------------------------------+
|                     Presentation Layer                      |
|                  (FastAPI, Routers, DTOs)                   |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                      Application Layer                      |
|               (Use Cases, Listeners, Workers)               |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                        Domain Layer                         |
|           (Entities, Ports/Interfaces, Services)            |
+-------------------------------------------------------------+
                               ^
                               |
+------------------------------+------------------------------+
|                     Infrastructure Layer                    |
|             (SQLAlchemy Models, DB Repos, Redis)            |
+-------------------------------------------------------------+
```

---

## Layer Separation and Responsibilities

### 1. Domain Layer (`domain/`)
The core domain holds the central business logic. It has zero external dependencies (no FastAPI, no SQLAlchemy, no Pydantic imports).
* **Entities**: Pure dataclasses expressing business structures and invariants.
* **Repositories (Ports)**: Abstract Interfaces (using `abc.ABC`) defining database access operations.
* **Events**: Immutable data representations of business occurrences (e.g. `UserRegistered`).
* **Services**: Cross-entity operational logic when transitions don't belong to a single entity.

### 2. Application Layer (`application/`)
Orchestrates domain elements to achieve system use cases.
* **Use Cases**: Interactors coordinating repositories, triggering domain behaviors, and checking rules.
* **Listeners**: Receivers processing events asynchronously (e.g., triggering notifications).
* **Tasks**: Async workers doing heavier processing.

### 3. Infrastructure Layer (`infrastructure/`)
Contains technology-specific implementations.
* **Models**: SQLAlchemy ORM mappings reflecting the physical database.
* **Repositories (Adapters)**: Implementations of the domain interfaces querying the database session.
* **UOW (Unit of Work)**: Coordinates write transactions.

### 4. Presentation Layer (`presentation/`)
Binds the system to external protocols.
* **Routers**: FastAPI routes parsing parameters and serializing return values.
* **Schemas**: Pydantic validations validating incoming payload structures.

---

## Cross-Module Communication rules
- **Loose Coupling**: Modules are distinct bounded contexts. Direct imports of another module's internal repository implementations, ORM models, or usecases are forbidden.
- **Dependency Injection**: Dependencies are wire-bound via `dependency-injector` containers per module context and loaded contextually.
