"""
Request-scoped context propagated via ContextVars.

Middleware populates these per request so cross-cutting concerns (e.g. the audit
writer, which runs deep inside the persistence layer with no access to the
`Request`) can attribute an action to the acting user and originating request
without threading those values through every call.
"""

from contextvars import ContextVar

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
actor_id_ctx: ContextVar[int | None] = ContextVar("actor_id", default=None)


def get_request_id() -> str | None:
    """Return the current request id (or None outside a request)."""
    return request_id_ctx.get()


def get_actor_id() -> int | None:
    """Return the current authenticated user id (or None if unauthenticated)."""
    return actor_id_ctx.get()
