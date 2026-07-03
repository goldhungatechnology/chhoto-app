from src.modules.workforce.domain.entities.team.team_entity import TeamEntity
from src.modules.workforce.domain.events.team.team_domain_events import (
    TeamCreatedEvent,
    TeamDeletedEvent,
    TeamUpdatedEvent,
)
from src.modules.workforce.domain.repositories.team.team_repository import (
    ITeamRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    ServerError,
)


class TeamDomainService:
    """
    Service class encapsulating Team domain logic.
    """

    def __init__(self, repository: ITeamRepository):
        self.repository = repository

    async def create_team(self, team_entity: TeamEntity) -> TeamEntity:
        """
        Creates a new team after enforcing uniqueness of the name within an organization
        and ensuring at most one default team per organization.
        """
        try:
            existing_team = await self.repository.get_by(
                name__ilike=team_entity.name,
                deleted_at=None,
            )
            if existing_team:
                raise ConflictError(
                    error=f"Team with name '{team_entity.name}' already exists in the organization"
                )

            if team_entity.is_default:
                existing_default = await self.repository.get_by(
                    is_default=True, deleted_at=None
                )
                if existing_default:
                    raise ConflictError(
                        error="A default team already exists for this organization"
                    )

            new_team = await self.repository.add(team_entity)
            if not new_team or not new_team.id:
                raise ServerError(error="Failed to create team")

            new_team.add_event(
                TeamCreatedEvent(
                    team_id=new_team.id,
                    organization_id=new_team.organization_id,
                    name=new_team.name,
                )
            )
            return new_team
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to create team", internal_details=str(e)
            ) from e

    async def get_team_by_uuid(self, team_uuid: str) -> TeamEntity:
        """
        Retrieves a team by its UUID. Raises NotFoundError when missing.
        """
        try:
            team = await self.repository.get_by_uuid(team_uuid)
            if not team or not team.is_active():
                raise NotFoundError(error="Team not found")
            return team
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to retrieve team", internal_details=str(e)
            ) from e

    async def list_teams_by_organization_id(
        self,
        *,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[TeamEntity], int]:
        """
        Page through active teams within the current organization scope,
        optionally filtered by status. Returns (teams, total).
        """
        try:
            return await self.repository.list_paginated(
                status=status,
                limit=limit,
                offset=offset,
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to list teams", internal_details=str(e)
            ) from e

    async def update_team(
        self,
        team_uuid: str,
        *,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
        timezone: str | None = None,
        is_default: bool | None = None,
        actor_id: int | None = None,
    ) -> TeamEntity:
        """
        Updates an existing team. Enforces unique name and single default constraints.
        """
        try:
            team = await self.get_team_by_uuid(team_uuid)

            if name is not None and name.lower() != team.name.lower():
                duplicate = await self.repository.get_by(
                    name__ilike=name, deleted_at=None
                )
                if duplicate and duplicate.id != team.id:
                    raise ConflictError(
                        error=f"Team with name '{name}' already exists in the organization"
                    )
                team.name = name

            if team.is_default and is_default is not False:
                raise ForbiddenError(
                    error="The default team cannot be updated",
                    errors={"name": "The default team cannot be updated"},
                )

            if description is not None:
                team.description = description
            if color is not None:
                team.color = color
            if timezone is not None:
                team.timezone = timezone

            if is_default is not None and is_default != team.is_default:
                if is_default:
                    existing_default = await self.repository.get_by(
                        is_default=True, deleted_at=None
                    )
                    if existing_default and existing_default.id != team.id:
                        raise ConflictError(
                            error="A default team already exists for this organization"
                        )
                    team.mark_as_default()
                else:
                    team.unmark_as_default()

            if actor_id is not None:
                team.set_updated_by(actor_id)
            team.mark_updated()

            updated_team = await self.repository.update(team)
            if not updated_team or not updated_team.id:
                raise ServerError(error="Failed to update team")

            updated_team.add_event(
                TeamUpdatedEvent(
                    team_id=updated_team.id,
                    organization_id=updated_team.organization_id,
                )
            )
            return updated_team
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to update team", internal_details=str(e)
            ) from e

    async def delete_team(self, team_uuid: str) -> TeamEntity:
        """
        Soft-deletes a team. Default teams cannot be deleted.
        """
        try:
            team = await self.get_team_by_uuid(team_uuid)

            if team.is_default:
                raise ConflictError(error="The default team cannot be deleted")

            team.soft_delete()
            team.mark_updated()

            updated_team = await self.repository.update(team)
            if not updated_team or not updated_team.id:
                raise ServerError(error="Failed to delete team")

            updated_team.add_event(
                TeamDeletedEvent(
                    team_id=updated_team.id,
                    organization_id=updated_team.organization_id,
                )
            )
            return updated_team
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to delete team", internal_details=str(e)
            ) from e
