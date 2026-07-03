from datetime import datetime
from typing import Any

from src.shared.schemas import BaseSchema


class AuditEventResponseSchema(BaseSchema):
    id: int
    uuid: str
    action: str
    entity_table: str
    entity_id: int | None
    organization_id: int | None
    before_data: dict[str, Any] | None
    after_data: dict[str, Any] | None
    actor_id: int | None
    request_id: str | None
    client_ip: str | None
    client_country: str | None
    client_city: str | None
    user_agent: str | None
    created_at: datetime


class AuditEventListResponseSchema(BaseSchema):
    items: list[AuditEventResponseSchema]
    total: int
    limit: int
    offset: int
