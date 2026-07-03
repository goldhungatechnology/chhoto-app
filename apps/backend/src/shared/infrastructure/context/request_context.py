"""
Request-scoped context propagated via ContextVars.
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
