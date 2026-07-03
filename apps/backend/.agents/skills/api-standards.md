# Skill: API Standards

This document establishes the API standards and interface rules for AI coding agents.

## Endpoint Naming
- Use `kebab-case` for paths. E.g., `/api/v1/auth/forgot-password`.
- Always structure resource routes using nouns (e.g., `/api/v1/users`, NOT `/api/v1/get-users`).

## API Contract Specifications
- Every endpoint must return responses conforming to the custom `CustomResponse` wrappers.
- Success Format:
  ```json
  {
    "success": true,
    "data": {},
    "message": "Operated successfully"
  }
  ```
- Error Format:
  ```json
  {
    "success": false,
    "error": "Error description header",
    "errors": { "field": "failure detail" }
  }
  ```

## Request Parameter Validations
- Validate input payloads explicitly using Pydantic models.
- Handle validation exceptions globally using `exception_handler.py`.
