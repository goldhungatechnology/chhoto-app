from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.workforce.application.seeders.default_roles import DEFAULT_ROLES
from src.modules.workforce.domain.entities.rbac.rbac_member_role_entity import (
    MemberRoleEntity,
)
from src.modules.workforce.domain.entities.rbac.rbac_role_entity import RoleEntity
from src.modules.workforce.domain.events.rbac.rbac_domain_events import (
    DefaultRolesAssignedEvent,
)
from src.modules.workforce.domain.services.rbac.rbac_member_role_domain_service import (
    RbacMemberRoleDomainService,
)
from src.modules.workforce.domain.services.rbac.rbac_role_domain_service import (
    RbacRoleDomainService,
)
from src.modules.workforce.infrastructure.uow.workforce_uow import WorkforceUOW
from src.modules.workforce.workforce_container import get_workforce_container
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.background_task_manager import bgtask
from src.shared.infrastructure.db import async_session
from src.shared.mediator.mediator import mediator


async def seed_default_roles_and_owner_membership(
    session: AsyncSession,
    organization_id: int,
    organization_member_id: int,
) -> None:
    """
    Seed the default roles for an organization and assign the owner role to the
    creating member. Runs against the caller's session so it can be composed
    into a larger transaction (the org-creation flow).
    """
    container = get_workforce_container(
        session=session, organization_id=organization_id
    )

    role_domain_service: RbacRoleDomainService = container.rbac_role_domain_service()
    member_role_domain_service: RbacMemberRoleDomainService = (
        container.rbac_member_role_domain_service()
    )

    for role in DEFAULT_ROLES:
        df_role = RoleEntity(
            name=role["name"],
            description=role["description"],
            is_system_role=role["is_system_role"],
            organization_id=organization_id,
        )

        new_role = await role_domain_service.create_role(df_role)

        for e in new_role.pull_events():
            await mediator.publish(e)

    owner_role = await role_domain_service.get_role_by_name(name="owner")
    if not owner_role or not owner_role.id:
        raise ServerError(
            "Owner role not found after creation",
            internal_details=f"Organization ID: {organization_id}",
        )

    nm_entity = MemberRoleEntity(
        member_id=organization_member_id,
        role_id=owner_role.id,
    )
    _ = await member_role_domain_service.create_member_role(nm_entity)

    await mediator.publish(
        DefaultRolesAssignedEvent(
            organization_id=organization_id,
        )
    )


async def _default_role_and_member_role_task(
    organization_id: int, organization_member_id: int
):
    """
    Background-task wrapper that opens its own session. Kept for callers that
    still need to run this work out-of-band; the org-creation flow now calls
    seed_default_roles_and_owner_membership inline.
    """
    try:
        async with async_session() as session:
            async with WorkforceUOW(session):
                await seed_default_roles_and_owner_membership(
                    session=session,
                    organization_id=organization_id,
                    organization_member_id=organization_member_id,
                )
    except Exception as e:
        raise ServerError(
            error="Failed to create default roles and member roles for the organization",
            internal_details=str(e),
        ) from e


default_role_and_member_role_task = bgtask.add_task(_default_role_and_member_role_task)
