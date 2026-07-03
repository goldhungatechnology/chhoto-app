from src.modules.workforce.domain.entities.team.team_member_entity import (
    TeamMemberEntity,
    TeamMemberRole,
)
from src.modules.workforce.domain.events.team.team_domain_events import (
    TeamMemberAddedEvent,
    TeamMemberRemovedEvent,
    TeamMemberRoleAssignedEvent,
)
from src.modules.workforce.domain.repositories.team.team_member_repository import (
    ITeamMemberRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    DomainError,
    InvalidError,
    NotFoundError,
    ServerError,
)


class TeamMemberDomainService:
    """
    Service class encapsulating TeamMember domain logic.
    """

    def __init__(self, repository: ITeamMemberRepository):
        self.repository = repository

    async def remove_all_members(self, team_id: int) -> None:
        """
        Remove every membership of a team (used when a team is deleted). Exposed
        on the domain service so the application layer doesn't reach into the
        repository directly.
        """
        await self.repository.bulk_delete_by_team_id(team_id)

    async def add_team_member(
        self,
        team_member_entity: TeamMemberEntity,
        *,
        organization_id: int,
        already_exists_failure: bool = True,
    ) -> TeamMemberEntity:
        """
        Adds a member to a team. Prevents duplicate (team_id, member_id) pairs.
        `organization_id` scopes the emitted audit event to the organization.
        """
        try:
            existing = await self.repository.get_by(
                team_id=team_member_entity.team_id,
                member_id=team_member_entity.member_id,
            )
            if existing and already_exists_failure:
                raise ConflictError(error="Member is already part of this team")

            if existing and not already_exists_failure:
                # If the membership already exists, return it without creating a
                # new one. This is useful for idempotent operations.
                return existing

            # Audit is recorded by the team-member event listeners (see the
            # audit module), so the automatic repository-level CRUD audit is
            # suppressed here to avoid duplicate audit rows.
            new_team_member = await self.repository.add(team_member_entity, audit=False)
            if not new_team_member or not new_team_member.id:
                raise ServerError(error="Failed to add team member")

            new_team_member.add_event(
                TeamMemberAddedEvent(
                    team_member_id=new_team_member.id,
                    organization_id=organization_id,
                    team_id=new_team_member.team_id,
                    member_id=new_team_member.member_id,
                    role=new_team_member.role,
                )
            )
            return new_team_member
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to add team member", internal_details=str(e)
            ) from e

    async def list_team_members(self, team_id: int) -> list[TeamMemberEntity]:
        """
        Lists all members of a team.
        """
        try:
            return await self.repository.list_by_team_id(team_id)
        except Exception as e:
            raise ServerError(
                error="Failed to list team members", internal_details=str(e)
            ) from e

    async def list_members_paginated(
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
        Lists team members across the organization with cursor-based pagination
        and optional filtering by team, role, organisation-member status, and
        text search (full name / email / username).
        """
        try:
            return await self.repository.list_paginated(
                organization_id=organization_id,
                team_id=team_id,
                role=role,
                status=status,
                search=search,
                cursor=cursor,
                limit=limit,
                direction=direction,
            )
        except Exception as e:
            raise ServerError(
                error="Failed to list team members", internal_details=str(e)
            ) from e

    async def list_members_by_team_ids(
        self, team_ids: list[int]
    ) -> list[TeamMemberEntity]:
        """
        Lists all memberships across the given teams, used to enrich team
        listings with their members and leaders.
        """
        try:
            return await self.repository.list_by_team_ids(team_ids)
        except Exception as e:
            raise ServerError(
                error="Failed to list team members", internal_details=str(e)
            ) from e

    async def remove_team_member(
        self,
        team_id: int,
        member_id: int,
        *,
        organization_id: int,
        allow_lead_removal: bool = False,
    ) -> TeamMemberEntity:
        """
        Removes a member from a team. Returns the removed entity carrying a
        TeamMemberRemovedEvent so the caller can publish it. `organization_id`
        scopes the emitted audit event to the organization.
        """
        try:
            existing = await self.repository.get_by(
                team_id=team_id, member_id=member_id
            )
            if not existing or not existing.id:
                raise NotFoundError(error="Team member not found")

            # A team enforces a single lead, so removing the lead outright would
            # silently leave the team leaderless. Require an explicit reassign
            # (set another member as team_lead) before the lead can be removed.
            if existing.role == TeamMemberRole.TEAM_LEAD and not allow_lead_removal:
                raise ConflictError(
                    error=(
                        "Cannot remove the team lead; assign a new team lead "
                        "before removing this member"
                    )
                )

            # Audit handled by the team-member event listeners; suppress the
            # automatic repository-level CRUD audit to avoid duplicate rows.
            await self.repository.delete(existing.id, audit=False)

            removed_event = TeamMemberRemovedEvent(
                team_member_id=existing.id,
                organization_id=organization_id,
                team_id=team_id,
                member_id=member_id,
                role=existing.role,
            )
            existing.add_event(removed_event)
            return existing
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to remove team member", internal_details=str(e)
            ) from e

    async def set_member_role(
        self,
        team_id: int,
        member_id: int,
        role: str,
        *,
        organization_id: int,
        actor_id: int | None = None,
    ) -> TeamMemberEntity:
        """
        Assigns a role to a team member. The member must already belong to the
        team. `role` must be one of TeamMemberRole.ALL. `organization_id` scopes
        the emitted audit event to the organization.
        """
        try:
            if role not in TeamMemberRole.ALL:
                raise InvalidError(error=f"Unknown team member role: {role}")

            existing = await self.repository.get_by(
                team_id=team_id, member_id=member_id
            )
            if not existing or not existing.id:
                raise NotFoundError(error="Team member not found")

            if existing.role == role:
                return existing

            existing.set_role(role)
            if actor_id is not None:
                existing.set_updated_by(actor_id)
            existing.mark_updated()

            # Audit handled by the team-member event listeners; suppress the
            # automatic repository-level CRUD audit to avoid duplicate rows.
            updated = await self.repository.update(existing, audit=False)
            if not updated or not updated.id:
                raise ServerError(error="Failed to set team member role")

            updated.add_event(
                TeamMemberRoleAssignedEvent(
                    team_member_id=updated.id,
                    organization_id=organization_id,
                    team_id=team_id,
                    member_id=member_id,
                    role=role,
                )
            )
            return updated
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to set team member role", internal_details=str(e)
            ) from e
