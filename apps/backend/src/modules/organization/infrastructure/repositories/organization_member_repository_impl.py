from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.modules.organization.domain.entities.organization_member_entity import (
    OrganizationMemberEntity,
)
from src.modules.organization.domain.repositories.organization_member_repository import (
    IOrganizationMemberRepository,
)
from src.modules.organization.infrastructure.models.organization_member_model import (
    OrganizationMemberModel,
)
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.repository.base_repository import BaseRepository


class OrganizationMemberRepositoryImpl(
    BaseRepository[OrganizationMemberEntity], IOrganizationMemberRepository
):
    """
    SQLAlchemy implementation of the organization member repository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = OrganizationMemberModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: OrganizationMemberEntity) -> dict:
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "organization_id": entity.organization_id,
            "user_id": entity.user_id,
            "status": entity.status,
            "created_by_id": entity.created_by_id,
            "updated_by_id": entity.updated_by_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> OrganizationMemberEntity:
        return OrganizationMemberEntity(
            id=row["id"],
            uuid=row["uuid"],
            organization_id=row["organization_id"],
            user_id=row["user_id"],
            status=row["status"],
            created_by_id=row.get("created_by_id"),
            updated_by_id=row.get("updated_by_id"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def list_paginated(
        self,
        *,
        organization_id: int,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[OrganizationMemberEntity], int]:
        where_clauses = ["organization_id = :organization_id"]
        params: dict[str, int | str] = {
            "organization_id": organization_id,
            "limit": limit,
            "offset": offset,
        }

        if status:
            where_clauses.append("status = :status")
            params["status"] = status

        where_sql = " AND ".join(where_clauses)

        list_sql = text(
            f"SELECT * FROM {self.table_name} WHERE {where_sql} "
            "ORDER BY id DESC LIMIT :limit OFFSET :offset"
        )
        count_sql = text(f"SELECT COUNT(*) FROM {self.table_name} WHERE {where_sql}")

        try:
            list_result = await self.session.execute(list_sql, params)
            rows = list_result.mappings().all()
            count_result = await self.session.execute(
                count_sql,
                {k: v for k, v in params.items() if k not in {"limit", "offset"}},
            )
            total = int(count_result.scalar_one())
            return [self.to_entity(dict(row)) for row in rows], total
        except Exception as e:
            raise ServerError(
                error="Failed to list organization members",
                internal_details=str(e),
            ) from e
