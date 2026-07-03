from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.modules.workforce.domain.entities.team.team_member_entity import (
    TeamMemberEntity,
    TeamMemberRole,
)
from src.modules.workforce.domain.repositories.team.team_member_repository import (
    ITeamMemberRepository,
)
from src.modules.workforce.infrastructure.models.team.team_member_model import (
    TeamMemberModel,
)
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.repository.base_repository import BaseRepository


class TeamMemberRepositoryImpl(BaseRepository[TeamMemberEntity], ITeamMemberRepository):
    """
    SQLAlchemy implementation of the team member repository interface.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = TeamMemberModel.__tablename__

        super().__init__(session=session, table_name=self.table_name)

    def to_row(self, entity: TeamMemberEntity) -> dict:
        """
        Convert a team member entity to a database row.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "team_id": entity.team_id,
            "member_id": entity.member_id,
            "role": entity.role,
            "created_by_id": entity.created_by_id,
            "updated_by_id": entity.updated_by_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> TeamMemberEntity:
        """
        Convert a database row to a team member entity.
        """
        return TeamMemberEntity(
            id=row["id"],
            uuid=row["uuid"],
            team_id=row["team_id"],
            member_id=row["member_id"],
            role=row.get("role", TeamMemberRole.MEMBER),
            created_by_id=row.get("created_by_id"),
            updated_by_id=row.get("updated_by_id"),
            created_at=row["created_at"],
            updated_at=row.get("updated_at"),
        )

    async def list_by_team_id(self, team_id: int) -> list[TeamMemberEntity]:
        """
        Lists all members of a specific team.
        """
        sql = text(f"SELECT * FROM {self.table_name} WHERE team_id = :team_id")

        try:
            result = await self.session.execute(sql, {"team_id": team_id})
            rows = result.mappings().all()
            return [self.to_entity(dict(row)) for row in rows]
        except Exception as e:
            raise ServerError(
                error="Failed to list team members", internal_details=str(e)
            ) from e

    async def list_by_team_ids(self, team_ids: list[int]) -> list[TeamMemberEntity]:
        """
        Lists all memberships across the given teams in a single query.
        Empty input short-circuits to avoid an empty IN-clause.
        """
        if not team_ids:
            return []

        sql = text(
            f"SELECT * FROM {self.table_name} "
            "WHERE team_id = ANY(:team_ids) ORDER BY id ASC"
        )

        try:
            result = await self.session.execute(sql, {"team_ids": team_ids})
            rows = result.mappings().all()
            return [self.to_entity(dict(row)) for row in rows]
        except Exception as e:
            raise ServerError(
                error="Failed to list team members", internal_details=str(e)
            ) from e

    async def list_paginated(
        self,
        *,
        organization_id: int,
        team_id: int | None = None,
        role: str | None = None,
        status: str | None = None,
        search: str | None = None,
        cursor: int | None = None,
        limit: int = 20,
        direction: str = "forward",
    ) -> tuple[list[TeamMemberEntity], str | None, str | None, bool, bool]:
        """
        Lists team members with cursor-based pagination and optional filtering.
        Joins through org_teams (org scoping), org_organization_members (status),
        and sys_auth_users (search). Returns a 5-tuple of
        (entities, prev_cursor, next_cursor, has_previous_page, has_next_page).
        """
        try:
            base_joins = (
                f"FROM {self.table_name} tm "
                "JOIN org_teams t ON tm.team_id = t.id "
                "JOIN org_organization_members om ON tm.member_id = om.id "
                "JOIN sys_auth_users u ON om.user_id = u.id"
            )

            where_clauses: list[str] = [
                "t.organization_id = :organization_id",
                "t.deleted_at IS NULL",
                "u.deleted_at IS NULL",
            ]
            params: dict = {"organization_id": organization_id}

            if team_id is not None:
                where_clauses.append("tm.team_id = :team_id")
                params["team_id"] = team_id

            if role is not None:
                where_clauses.append("tm.role = :role")
                params["role"] = role

            if status is not None:
                where_clauses.append("om.status = :status")
                params["status"] = status

            if search is not None and search.strip():
                pattern = f"%{search.strip()}%"
                where_clauses.append(
                    "(u.full_name ILIKE :search OR u.email ILIKE :search OR u.username ILIKE :search)"
                )
                params["search"] = pattern

            if direction == "backward" and cursor is not None:
                where_clauses.append("tm.id < :cursor")
                params["cursor"] = cursor
                order_clause = "ORDER BY tm.id DESC"
            elif direction == "forward" and cursor is not None:
                where_clauses.append("tm.id > :cursor")
                params["cursor"] = cursor
                order_clause = "ORDER BY tm.id ASC"
            else:
                order_clause = "ORDER BY tm.id ASC"

            where_sql = " AND ".join(where_clauses)
            params["fetch_limit"] = limit + 1

            sql = text(
                f"SELECT tm.* {base_joins} WHERE {where_sql} {order_clause} "
                "LIMIT :fetch_limit"
            )

            result = await self.session.execute(sql, params)
            rows = result.mappings().all()

            has_more = len(rows) > limit
            if has_more:
                rows = rows[:limit]

            entities = [self.to_entity(dict(row)) for row in rows]

            if direction == "backward":
                entities.reverse()

            prev_cursor: str | None = None
            next_cursor: str | None = None
            has_previous_page = False
            has_next_page = False

            if entities:
                if direction == "forward":
                    has_next_page = has_more
                    if cursor is not None:
                        prev_cursor = str(cursor)
                        has_previous_page = True
                    if has_next_page:
                        next_cursor = str(entities[-1].id)
                else:
                    has_previous_page = has_more
                    if cursor is not None:
                        next_cursor = str(cursor)
                        has_next_page = True
                    if has_previous_page:
                        prev_cursor = str(entities[0].id)

            return entities, prev_cursor, next_cursor, has_previous_page, has_next_page

        except Exception as e:
            raise ServerError(
                error="Failed to list team members", internal_details=str(e)
            ) from e

    async def bulk_delete_by_team_id(self, team_id: int) -> None:
        """
        Removes all members of a specific team.
        """
        sql = text(f"DELETE FROM {self.table_name} WHERE team_id = :team_id")

        try:
            await self.session.execute(sql, {"team_id": team_id})
            await self.session.flush()
        except Exception as e:
            raise ServerError(
                error="Failed to bulk delete team members",
                internal_details=str(e),
            ) from e
