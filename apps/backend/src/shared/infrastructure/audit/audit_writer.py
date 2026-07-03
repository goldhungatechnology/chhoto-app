import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.settings import config
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.context.request_context import (
    get_actor_id,
    get_request_id,
)
from src.shared.infrastructure.logger import logger

SENSITIVE_KEYS = {
    "password",
    "hashed_password",
    "token",
    "secret",
    "api_key",
    "access_token",
    "refresh_token",
    "authorization",
}


def _is_sensitive_key(key: str) -> bool:
    key_normalized = key.lower().replace("-", "_")
    if key_normalized in SENSITIVE_KEYS:
        return True
    return any(token in key_normalized for token in SENSITIVE_KEYS)


def sanitize_payload(value: Any) -> Any:
    """
    Converts complex data into JSON-safe representation and redacts sensitive fields.
    """
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if _is_sensitive_key(str(key)):
                sanitized[str(key)] = "[REDACTED]"
                continue
            sanitized[str(key)] = sanitize_payload(item)
        return sanitized

    if isinstance(value, list):
        return [sanitize_payload(item) for item in value]

    if isinstance(value, tuple):
        return [sanitize_payload(item) for item in value]

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return str(value)

    return value


async def write_audit_event(
    *,
    session: AsyncSession | None = None,
    action: str,
    entity_table: str,
    entity_id: int | None,
    before_data: dict[str, Any] | None,
    after_data: dict[str, Any] | None,
    client_ip: str | None = None,
    client_country: str | None = None,
    client_city: str | None = None,
    user_agent: str | None = None,
) -> None:
    """
    Writes an append-only audit event to sys_audit_logs.
    """
    from src.shared.infrastructure.db import async_session

    if not config.AUDIT_ENABLED:
        return

    organization_id = _resolve_organization_id(
        entity_table=entity_table,
        entity_id=entity_id,
        before_data=before_data,
        after_data=after_data,
    )

    sql = text(
        "INSERT INTO sys_audit_logs (uuid, action, entity_table, entity_id, "
        "organization_id, before_data, after_data, actor_id, request_id, client_ip, client_country, client_city, user_agent) "
        "VALUES (:uuid, :action, :entity_table, :entity_id, :organization_id, :before_data, :after_data, "
        ":actor_id, :request_id, :client_ip, :client_country, :client_city, :user_agent)"
    )

    payload = {
        "uuid": str(uuid4()),
        "action": action,
        "entity_table": entity_table,
        "entity_id": entity_id,
        "organization_id": organization_id,
        "before_data": (
            json.dumps(sanitize_payload(before_data), ensure_ascii=True)
            if before_data is not None
            else None
        ),
        "after_data": (
            json.dumps(sanitize_payload(after_data), ensure_ascii=True)
            if after_data is not None
            else None
        ),
        # Attribute the action to the acting user / originating request, read
        # from the request-scoped ContextVars set by middleware.
        "actor_id": get_actor_id(),
        "request_id": get_request_id(),
        "client_ip": client_ip,
        "client_country": client_country,
        "client_city": client_city,
        "user_agent": user_agent,
    }

    try:
        if session is not None:
            # Caller owns the transaction (UoW commits/rolls back).
            await session.execute(sql, payload)
        else:
            # Self-managed: open, commit and close our own session so the
            # pooled connection is always released (no leak on this path).
            async with async_session() as own_session:
                await own_session.execute(sql, payload)
                await own_session.commit()
    except Exception as e:
        logger.error(
            "[Audit] Failed to write audit event action=%s table=%s id=%s: %s",
            action,
            entity_table,
            str(entity_id),
            str(e),
        )
        if config.AUDIT_STRICT_MODE:
            raise ServerError(
                error="Failed to persist audit event",
                internal_details=str(e),
            ) from e


def _resolve_organization_id(
    *,
    entity_table: str,
    entity_id: int | None,
    before_data: dict[str, Any] | None,
    after_data: dict[str, Any] | None,
) -> int | None:
    """
    Resolve organization scope from known data shapes.
    """
    for data in (after_data, before_data):
        if not data:
            continue
        org_id = data.get("organization_id")
        if isinstance(org_id, int):
            return org_id

    if entity_table == "org_organizations" and isinstance(entity_id, int):
        return entity_id

    return None
