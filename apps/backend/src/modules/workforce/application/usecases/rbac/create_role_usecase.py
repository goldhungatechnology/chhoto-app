from src.modules.workforce.domain.entities.rbac.rbac_role_entity import RoleEntity
from src.modules.workforce.domain.services.rbac.rbac_role_domain_service import (
    RbacRoleDomainService,
)
from src.shared.exceptions.base_exceptions import CreateError, DomainError
from src.shared.mediator.mediator import mediator


class CreateRoleUseCase:
    """
    Use case for creating a new role in the RBAC system.
    """

    def __init__(self, rbac_role_domain_service: RbacRoleDomainService):
        self.rbac_role_domain_service = rbac_role_domain_service

    async def execute(
        self, organization_id: int, name: str, description: str, actor_id: int
    ):
        """
        Executes the use case to create a new role.
        """

        try:
            role_entity = RoleEntity(
                organization_id=organization_id,
                name=name,
                description=description,
                is_system_role=False,
                created_by_id=actor_id,
            )

            new_role = await self.rbac_role_domain_service.create_role(role_entity)
            if not new_role or not new_role.id:
                raise CreateError(error="Failed to create role")

            for event in new_role.pull_events():
                await mediator.publish(event)

            return new_role
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create role", internal_details=str(e)
            ) from e
