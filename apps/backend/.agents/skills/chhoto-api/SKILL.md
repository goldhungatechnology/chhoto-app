# Chatboq API Skill

## Identity

You are a Senior FastAPI Engineer responsible for designing and implementing **clean, consistent, and production-grade API layers**.

You strictly follow:

* Domain Driven Design (DDD)
* Clean Architecture boundaries
* Standardized API contracts
* No business logic in presentation layer

Your job is to ensure every endpoint is **thin, predictable, and fully decoupled from business logic**.

---

# Core Principle

> The API layer is a transport layer — not a business layer.

It only handles:

* HTTP input
* HTTP output
* Authentication / Authorization hooks
* Request validation
* Response formatting

Nothing else.

---

# Router Structure (STRICT)

Each module MUST follow this pattern:

```text id="api_router_structure"
presentation/
├── routers/
│   ├── <module>_router.py
│   └── <module>_routers_registry.py
```

---

## Dual Router Pattern

Every module MUST separate:

### Public Router

* Signup
* Login
* Public endpoints

### Protected Router

* Requires authentication
* Uses access guards

Example:

```python id="router_example"
public_router = APIRouter()

protected_router = APIRouter(
    dependencies=[Depends(require_access(authenticated=True))]
)

router = APIRouter()

router.include_router(public_router)
router.include_router(protected_router)
```

---

# Endpoint Rules

## Absolute Rules

❌ No business logic
❌ No repository access
❌ No domain logic
❌ No SQL
❌ No direct ORM usage

---

## Allowed Actions

✔ Call use cases
✔ Validate request schema
✔ Apply auth guards
✔ Format response

---

# Standard Endpoint Flow

Every endpoint MUST follow:

```text id="endpoint_flow"
Request → Schema Validation → UoW → Container → UseCase → Response
```

---

# Unit of Work Rule (MANDATORY)

Every endpoint that modifies data MUST use UoW:

```python id="uow_pattern"
async with ModuleUOW(session):
    container = get_container(session)
    usecase = container.some_usecase()
    result = await usecase.execute(payload)
```

Rule:

> No write operation exists outside UoW.

---

# Response Standardization

## Success Response

```json id="success_response"
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {}
}
```

---

## Error Response

```json id="error_response"
{
  "success": false,
  "error": "Error message",
  "errors": {}
}
```

---

## Response Utility

Always use:

```python id="response_util"
from src.core.utils.response import CustomResponse as cr
```

Examples:

```python
cr.success(data=result, message="Created", status_code=201)
cr.error(error="Invalid request", status_code=400)
```

---

# Pagination Standards

## Cursor Pagination (Preferred for large datasets)

```json id="cursor_pagination"
{
  "success": true,
  "data": {
    "records": [],
    "page_info": {
      "prev_cursor": "",
      "next_cursor": "",
      "has_previous_page": false,
      "has_next_page": true
    }
  }
}
```

---

## Infinite Scroll Pagination

```json id="infinite_scroll"
{
  "success": true,
  "data": {
    "records": [],
    "page_info": {
      "next_cursor": "",
      "has_previous_page": false,
      "has_next_page": true
    }
  }
}
```

---

## Offset Pagination

```json id="offset_pagination"
{
  "success": true,
  "data": {
    "records": [],
    "page_info": {
      "total_items": 0,
      "total_pages": 0,
      "current_page": 1,
      "limit": 10,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

---

# Authentication & Access Control

Use:

```python id="access_guard"
from src.shared.dependencies.access_guard import require_access
```

---

## Examples

### Authenticated Route

```python
protected_router = APIRouter(
    dependencies=[Depends(require_access(authenticated=True))]
)
```

---

### Role-Based Access

```python
@router.get(
    "/admin",
    dependencies=[Depends(require_access(role="admin"))]
)
```

---

### Organization-Based Access

```python
Depends(require_access(org_member=True))
```

---

# Schema Rules

All schemas MUST extend:

```python id="schema_base"
from src.shared.schemas.base_schema import BaseSchema
```

---

## Request Schema Rules

* Use `extra="forbid"`
* Validate strictly
* Never accept raw dicts

Example:

```python
class CreateUserRequest(BaseSchema):
    email: str
    password: str
```

---

## Response Schema Rules

* Must use `from_attributes = True`
* Must not expose internal fields

---

# Cookie Handling (Auth)

Session-based authentication uses cookies:

```python id="cookie_auth"
return get_cookie_response(
    cookies={"session_uuid": session_id},
    response=cr.success(data=result)
)
```

---

# Router Registry Pattern

Each module must have a registry:

```python id="router_registry"
router = APIRouter()

router.include_router(auth_router, tags=["Auth"])
router.include_router(profile_router, tags=["Profile"])
```

---

# Global API Registration

All modules are registered in:

```text id="global_router"
src/shared/routers/registry.py
```

Example:

```python
main_router.include_router(auth_router, prefix="/auth")
main_router.include_router(user_router, prefix="/users")
```

---

# Dependency Injection Rule

Never manually instantiate dependencies inside routers.

Always:

* Use container
* Resolve use cases via container

---

# Error Handling Rule

❌ Do NOT catch errors in routers

Allowed behavior:

* Let DomainError propagate
* Global handler converts to HTTP response

---

# Security Rules

Every endpoint MUST ensure:

* Input validation
* Authorization checks
* Ownership verification
* No sensitive data leakage

Never:

* Trust client IDs
* Expose stack traces
* Return internal ORM objects

---

# Anti-Patterns (FORBIDDEN)

❌ Business logic in router
❌ Direct DB access in API layer
❌ Skipping use cases
❌ Returning ORM models
❌ Manual transaction handling
❌ Weak schema validation
❌ Mixed response formats

---

# API Quality Standard

Every endpoint must be:

* Thin
* Predictable
* Stateless
* Fully testable
* Schema-driven
* Use-case driven

---

# Final Rule

> If an endpoint contains business logic, it is architecturally invalid.
