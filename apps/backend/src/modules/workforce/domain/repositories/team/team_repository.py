from abc import abstractmethod

from src.modules.workforce.domain.entities.team.team_entity import TeamEntity
from src.shared.domain.repository.organization_repository_interface import (
    IOrganizationRepository,
)


class ITeamRepository(IOrganizationRepository[TeamEntity]):
    """
    Repository interface for managing TeamEntity instances.
    """

    @abstractmethod
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
