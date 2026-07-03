# Coding Standards and Conventions

This document outlines the coding standards, formatting guidelines, and best practices that developers must adhere to.

## General Coding Principles
* **Explicit Over Implicit**: Write clear, easy-to-read code. Avoid magic behavior and runtime patches.
* **Typing Checks**: All parameters and return values must be explicitly typed using Python type hints. The project relies on Pyright/MyPy for type verification.
* **Separation of Concerns**: Do not mix serialization (Pydantic), persistence (SQLAlchemy), and domain logic (Entities) in single files.

---

## Naming Conventions

| Entity | Pattern | Example |
| :--- | :--- | :--- |
| **Folders / Modules** | `snake_case` | `auth`, `team_management` |
| **Files** | `snake_case` | `user_repository_impl.py` |
| **Classes** | `PascalCase` | `LoginUseCase`, `UserRepositoryImpl` |
| **Functions / Methods** | `snake_case` | `get_by_email()`, `execute()` |
| **Constants** | `SCREAMING_SNAKE_CASE`| `DATABASE_URL`, `TOKEN_TTL` |
| **HTTP Routes** | `kebab-case` | `/api/v1/auth/forgot-password` |
| **Database Tables** | `snake_case` | `sys_auth_users` |

---

## API Contract Conventions

All endpoints must return structured responses adhering to the following formats:

### Success Response
```json
{
  "success": true,
  "data": { ... } or [ ... ] or null,
  "message": "Description of success"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error header detail message",
  "errors": {
    "field_name": "Specific validation failure message"
  } or null
}
```

---

## Error Handling Standards
- Always raise domain-specific exceptions (derived from `DomainError` in `src.shared.exceptions.base_exceptions`) rather than generic exceptions.
- Do not let raw database exceptions propagate to the presentation layer. Use the global exception handler mapping to safely log errors and translate them to HTTP status responses.
