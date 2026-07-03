from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.workforce.application.seeders.default_teams import DEFAULT_TEAMS
from src.modules.workforce.domain.entities.team.team_entity import TeamEntity
from src.modules.workforce.domain.entities.team.team_member_entity import (
    TeamMemberEntity,
    TeamMemberRole,
)
from src.modules.workforce.domain.services.team.team_domain_service import (
    TeamDomainService,
)
from src.modules.workforce.domain.services.team.team_member_domain_service import (
    TeamMemberDomainService,
)
from src.modules.workforce.infrastructure.uow.workforce_uow import WorkforceUOW
from src.modules.workforce.workforce_container import get_workforce_container
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.background_task_manager import bgtask
from src.shared.infrastructure.db import async_session
from src.shared.mediator.mediator import mediator


async def seed_default_teams(
    session: AsyncSession,
    organization_id: int,
    organization_member_id: int,
) -> None:
    """
    Seed the default team(s) for an organization and add the creating member to
    the default team as team lead. Runs against the caller's session so it can
    be composed into a larger transaction.
    """
    container = get_workforce_container(
        session=session, organization_id=organization_id
    )

    team_domain_service: TeamDomainService = container.team_domain_service()
    team_member_domain_service: TeamMemberDomainService = (
        container.team_member_domain_service()
    )

    for team_data in DEFAULT_TEAMS:
        team_entity = TeamEntity(
            name=team_data["name"],
            description=team_data["description"],
            color=team_data["color"],
            timezone=team_data["timezone"],
            is_default=team_data["is_default"],
            organization_id=organization_id,
        )

        new_team = await team_domain_service.create_team(team_entity)
        if not new_team or not new_team.id:
            raise ServerError(
                error="Failed to create default team",
                internal_details=(
                    f"Organization ID: {organization_id}, Team: {team_data['name']}"
                ),
            )

        for event in new_team.pull_events():
            await mediator.publish(event)

        if new_team.is_default:
            team_member_entity = TeamMemberEntity(
                team_id=new_team.id,
                member_id=organization_member_id,
                role=TeamMemberRole.TEAM_LEAD,
            )
            new_team_member = await team_member_domain_service.add_team_member(
                team_member_entity, organization_id=organization_id
            )

            for event in new_team_member.pull_events():
                await mediator.publish(event)


async def _default_team_task(organization_id: int, organization_member_id: int):
    """
    Background-task wrapper that opens its own session. Kept for callers that
    still need to run this work out-of-band; the org-creation flow now calls
    seed_default_teams inline.
    """
    try:
        async with async_session() as session:
            async with WorkforceUOW(session):
                await seed_default_teams(
                    session=session,
                    organization_id=organization_id,
                    organization_member_id=organization_member_id,
                )
    except Exception as e:
        raise ServerError(
            error="Failed to create default team for the organization",
            internal_details=str(e),
        ) from e


default_team_task = bgtask.add_task(_default_team_task)
