# Skill: Backend Architecture Guide

This document serves as the guide for AI agents working on the backend architecture.

## Architecture Guidelines
- **Core Philosophy**: Domain-Driven Design (DDD) combined with Clean Architecture.
- **Layer Isolation**:
  - `domain`: Contains pure business entities, repository ports (interfaces), and value objects. No framework dependencies.
  - `application`: Holds use cases coordinate domain actions. Must only depend on interfaces, not implementations.
  - `infrastructure`: Contains database models, database repository implementations, cache services, and external client configurations.
  - `presentation`: Houses FastAPI controllers, routers, request/response models (Pydantic schemas), and middleware.

## Forbidden Patterns (Anti-patterns)
- ❌ Do NOT import SQLAlchemy, FastAPI, or Pydantic inside the `domain` layer.
- ❌ Do NOT execute raw SQL or perform database transactions directly inside use cases. Always use the Unit of Work (`BaseUOW`) wrapper.
- ❌ Do NOT return database models (`Base` mappings) directly to the client. Always convert ORM models to domain entities, and then presentation schemas.
