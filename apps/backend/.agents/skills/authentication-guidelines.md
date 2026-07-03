# Skill: Authentication Guidelines

This document guides the implementation of authentication features.

## Architecture Blueprint
- **Session-based Authentication**: Prefer secure session cookie management over local storage tokens.
- **Cookies security**: Set session cookies with `httponly=True`, `secure=True`, and `samesite="lax"` or `samesite="none"` (depending on environment/CORS).
- **Passwords Hashing**: Always hash passwords using `Argon2` or similar strong algorithms. Do NOT store raw passwords.

## Implementation Checklist
- Write SQLAlchemy schemas under `infrastructure/models/user_model.py`.
- Inherit and implement user lookup inside `infrastructure/repositories/user_repository_impl.py`.
- Define login validation DTOs inside `presentation/schemas/auth_schemas.py`.
- Map dependency providers inside `auth_container.py` and register the module container.
- Update `AuthMiddleware` to perform active validation of the session cookie against the database session.
