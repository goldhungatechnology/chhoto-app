from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.modules.workforce.domain.entities.team.team_entity import TeamEntity
from src.modules.workforce.domain.repositories.team.team_repository import (
    ITeamRepository,
)
from src.modules.workforce.infrastructure.models.team.team_model import TeamModel
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.repository.organization_repository import (
    OrganizationRepository,
)


class TeamRepositoryImpl(OrganizationRepository[TeamEntity], ITeamRepository):
    """
    SQLAlchemy implementation of the team repository interface.
    """

    def __init__(self, session: AsyncSession, organization_id: int):
        self.session = session
        self.organization_id = organization_id
        self.table_name = TeamModel.__tablename__

        super().__init__(
            session=session,
            table_name=self.table_name,
            organization_id=organization_id,
        )

    def to_row(self, entity: TeamEntity) -> dict:
        """
        Convert a team entity to a database row.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "name": entity.name,
            "description": entity.description,
            "color": entity.color,
            "timezone": entity.timezone,
            "is_default": entity.is_default,
            "status": entity.status,
            "organization_id": entity.organization_id,
            "created_by_id": entity.created_by_id,
            "updated_by_id": entity.updated_by_id,
            "deleted_at": entity.deleted_at,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> TeamEntity:
        """
        Convert a database row to a team entity.
        """
        return TeamEntity(
            id=row["id"],
            uuid=row["uuid"],
            name=row["name"],
            description=row.get("description"),
            color=row.get("color"),
            timezone=row.get("timezone"),
            is_default=row.get("is_default", False),
            status=row.get("status", "active"),
            organization_id=row["organization_id"],
            created_by_id=row.get("created_by_id"),
            updated_by_id=row.get("updated_by_id"),
            deleted_at=row.get("deleted_at"),
            created_at=row["created_at"],
            updated_at=row.get("updated_at"),
        )

    async def list_paginated(
        self,
        *,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[TeamEntity], int]:
        """
        Page through active (non-soft-deleted) teams within the organization
        scope, optionally filtered by status. Returns (teams, total).
        """
        where_clauses = [self._org_filter_sql(), "deleted_at IS NULL"]
        params: dict[str, int | str] = {
            **self._org_params(),
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
                error="Failed to list teams",
                internal_details=str(e),
            ) from e
