from src.modules.workforce.domain.entities.rbac.rbac_role_entity import RoleEntity
from src.modules.workforce.domain.events.rbac.rbac_domain_events import RoleCreatedEvent
from src.modules.workforce.domain.repositories.rbac.rbac_role_repository import (
    IRoleRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    DomainError,
    ServerError,
)


class RbacRoleDomainService:
    """
    service class for RBAC Role domain logic
    """

    def __init__(self, repository: IRoleRepository):
        self.repository = repository

    async def create_role(self, role_entity: RoleEntity) -> RoleEntity:
        """
        Creates a new role.
        """
        try:
            existing_role = await self.repository.get_by(
                name__ilike=role_entity.name,
                organization_id=role_entity.organization_id,
            )
            if existing_role:
                raise ConflictError(
                    error=f"Role with name '{role_entity.name}' already exists in the organization"
                )

            new_role = await self.repository.add(role_entity)
            if not new_role or not new_role.id:
                raise ServerError(error="Failed to create role")
            new_role.add_event(
                RoleCreatedEvent(
                    organization_id=new_role.organization_id,
                    role_id=new_role.id,
                    name=new_role.name,
                )
            )
            return new_role
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to create role", internal_details=str(e)
            ) from e

    async def get_role_by_id(self, role_id: int) -> RoleEntity | None:
        """
        Retrieves a role by its ID
        """
        try:
            return await self.repository.get_by(id=role_id)
        except Exception as e:
            raise ServerError(
                error="Failed to retrieve role", internal_details=str(e)
            ) from e

    async def get_role_by_uuid(self, role_uuid: str) -> RoleEntity | None:
        """
        Retrieves a role by its UUID.
        """
        try:
            return await self.repository.get_by_uuid(role_uuid)
        except Exception as e:
            raise ServerError(
                error="Failed to retrieve role", internal_details=str(e)
            ) from e

    async def get_role_by_name(self, name: str) -> RoleEntity | None:
        """
        Retrieves roles by their name
        """
        try:
            return await self.repository.get_by(name__ilike=name)
        except Exception as e:
            raise ServerError(
                error="Failed to retrieve roles", internal_details=str(e)
            ) from e

    async def list_roles_by_organization_id(self) -> list[RoleEntity]:
        """
        Lists all roles
        """
        try:
            return await self.repository.filter(name__ne="owner")
        except Exception as e:
            raise ServerError(
                error="Failed to list roles", internal_details=str(e)
            ) from e
