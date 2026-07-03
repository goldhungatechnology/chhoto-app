from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from src.shared.infrastructure.audit.audit_writer import (
    _resolve_organization_id,
    sanitize_payload,
    write_audit_event,
)


def test_sanitize_payload_redacts_sensitive_keys():
    payload = {
        "email": "test@example.com",
        "password": "plain",
        "nested": {
            "token": "abc",
            "safe": "value",
        },
    }

    sanitized = sanitize_payload(payload)

    assert sanitized["email"] == "test@example.com"
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["nested"]["token"] == "[REDACTED]"
    assert sanitized["nested"]["safe"] == "value"


def test_sanitize_payload_redacts_sensitive_key_variants():
    payload = {
        "hashedPassword": "x",
        "oauth_access_token": "y",
        "db_secret_value": "z",
    }

    sanitized = sanitize_payload(payload)

    assert sanitized["hashedPassword"] == "[REDACTED]"
    assert sanitized["oauth_access_token"] == "[REDACTED]"
    assert sanitized["db_secret_value"] == "[REDACTED]"


def test_sanitize_payload_serializes_datetime():
    now = datetime.now(UTC)
    sanitized = sanitize_payload({"occurred_at": now})
    assert sanitized["occurred_at"] == now.isoformat()


@pytest.mark.asyncio
@patch("src.shared.infrastructure.audit.audit_writer.config")
async def test_write_audit_event_executes_insert(mock_config):
    mock_config.AUDIT_ENABLED = True
    session = AsyncMock()
    await write_audit_event(
        session=session,
        action="create",
        entity_table="sys_auth_users",
        entity_id=1,
        before_data=None,
        after_data={"password": "secret"},
    )

    assert session.execute.await_count == 1


def test_resolve_organization_id_from_payload():
    organization_id = _resolve_organization_id(
        entity_table="org_organization_members",
        entity_id=1,
        before_data=None,
        after_data={"organization_id": 99},
    )
    assert organization_id == 99


def test_resolve_organization_id_for_organization_table():
    organization_id = _resolve_organization_id(
        entity_table="org_organizations",
        entity_id=55,
        before_data=None,
        after_data=None,
    )
    assert organization_id == 55
