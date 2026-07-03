from abc import abstractmethod

from src.modules.workforce.domain.entities.team.team_member_entity import (
    TeamMemberEntity,
)
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class ITeamMemberRepository(IBaseRepository[TeamMemberEntity]):
    """
    Repository interface for managing TeamMemberEntity instances.
    """

    @abstractmethod
    async def list_by_team_id(self, team_id: int) -> list[TeamMemberEntity]:
        """
        Lists all members of a specific team.
        """

    @abstractmethod
    async def list_by_team_ids(self, team_ids: list[int]) -> list[TeamMemberEntity]:
        """
        Lists all memberships across the given teams in a single query. Used to
        enrich team listings with their members (and leaders) without an N+1
        query per team.
        """

    @abstractmethod
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
        Returns (entities, prev_cursor, next_cursor, has_previous_page, has_next_page).
        """

    @abstractmethod
    async def bulk_delete_by_team_id(self, team_id: int) -> None:
        """
        Removes all members from a specific team.
        """
