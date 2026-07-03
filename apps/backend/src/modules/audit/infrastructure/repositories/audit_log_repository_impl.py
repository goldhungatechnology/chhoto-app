import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.audit.domain.entities.audit_log_entity import AuditLogEntity
from src.modules.audit.domain.repositories.audit_log_repository import (
    IAuditLogRepository,
)
from src.modules.audit.infrastructure.models.audit_log_model import AuditLogModel
from src.shared.infrastructure.repository.base_repository import BaseRepository


class AuditLogRepositoryImpl(BaseRepository[AuditLogEntity], IAuditLogRepository):
    """
    SQLAlchemy implementation for audit-log repository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = AuditLogModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: AuditLogEntity) -> dict:
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "action": entity.action,
            "entity_table": entity.entity_table,
            "entity_id": entity.entity_id,
            "organization_id": entity.organization_id,
            "before_data": (
                json.dumps(entity.before_data, ensure_ascii=True)
                if entity.before_data is not None
                else None
            ),
            "after_data": (
                json.dumps(entity.after_data, ensure_ascii=True)
                if entity.after_data is not None
                else None
            ),
            "actor_id": entity.actor_id,
            "request_id": entity.request_id,
            "client_ip": entity.client_ip,
            "client_country": entity.client_country,
            "client_city": entity.client_city,
            "user_agent": entity.user_agent,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> AuditLogEntity:
        return AuditLogEntity(
            id=row["id"],
            uuid=row["uuid"],
            action=row["action"],
            entity_table=row["entity_table"],
            entity_id=row.get("entity_id"),
            organization_id=row.get("organization_id"),
            before_data=json.loads(row["before_data"])
            if row.get("before_data")
            else None,
            after_data=json.loads(row["after_data"]) if row.get("after_data") else None,
            actor_id=row.get("actor_id"),
            request_id=row.get("request_id"),
            client_ip=row.get("client_ip"),
            client_country=row.get("client_country"),
            client_city=row.get("client_city"),
            user_agent=row.get("user_agent"),
            created_at=row["created_at"],
            updated_at=row.get("updated_at"),
        )

    async def list_events(
        self,
        *,
        organization_id: int,
        action: str | None = None,
        entity_table: str | None = None,
        actor_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AuditLogEntity], int]:
        where_clauses = ["organization_id = :organization_id"]
        params: dict[str, int | str] = {
            "organization_id": organization_id,
            "limit": limit,
            "offset": offset,
        }

        if action:
            where_clauses.append("action = :action")
            params["action"] = action
        if entity_table:
            where_clauses.append("entity_table = :entity_table")
            params["entity_table"] = entity_table
        if actor_id is not None:
            where_clauses.append("actor_id = :actor_id")
            params["actor_id"] = actor_id

        where_sql = " AND ".join(where_clauses)

        list_sql = text(
            f"SELECT * FROM {self.table_name} WHERE {where_sql} "
            "ORDER BY id DESC LIMIT :limit OFFSET :offset"
        )
        count_sql = text(f"SELECT COUNT(*) FROM {self.table_name} WHERE {where_sql}")

        list_result = await self.session.execute(list_sql, params)
        rows = list_result.mappings().all()
        count_result = await self.session.execute(
            count_sql, {k: v for k, v in params.items() if k not in {"limit", "offset"}}
        )
        total = int(count_result.scalar_one())

        return [self.to_entity(dict(row)) for row in rows], total
