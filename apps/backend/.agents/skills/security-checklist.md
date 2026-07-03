# Skill: Security Checklist

This document details security requirements that must be checked when building backend features.

## Data Validation
- [ ] Inputs must be explicitly validated using Pydantic schemas.
- [ ] Sanitize any raw inputs before persistence to prevent injection attacks.

## Database & Session Security
- [ ] Production credentials must NEVER be checked into source code. Always use `pydantic-settings` to reject insecure defaults when `ENVIRONMENT=production`.
- [ ] Session cookies must be `HttpOnly`, `Secure`, and have appropriate `SameSite` policy.

## Secrets and Hashing
- [ ] Hashing of sensitive inputs (e.g. passwords) must use strong algorithms (e.g., Argon2).
- [ ] Secret keys must be loaded from securely populated environment variables.
