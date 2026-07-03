from dataclasses import dataclass, field
from typing import Any

from src.shared.domain.entity.base_entity import BaseEntity


@dataclass(kw_only=True)
class AuditLogEntity(BaseEntity):
    """
    Entity representing append-only audit events.
    """

    action: str = field(metadata={"description": "create|update|delete|action"})
    entity_table: str = field(metadata={"description": "Audited table name"})
    entity_id: int | None = None
    organization_id: int | None = None
    before_data: dict[str, Any] | None = None
    after_data: dict[str, Any] | None = None
    actor_id: int | None = None
    request_id: str | None = None
    client_ip: str | None = None
    client_country: str | None = None
    client_city: str | None = None
    user_agent: str | None = None
