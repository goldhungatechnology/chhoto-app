from src.modules.workforce.domain.entities.rbac.rbac_member_role_entity import (
    MemberRoleEntity,
)
from src.modules.workforce.domain.events.rbac.rbac_domain_events import (
    MemberRoleCreatedEvent,
)
from src.modules.workforce.domain.repositories.rbac.rbac_member_role_repository import (
    IMemberRoleRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    DomainError,
    ServerError,
)


class RbacMemberRoleDomainService:
    """
    service class for RBAC member role domain logic
    """

    def __init__(self, repository: IMemberRoleRepository):
        self.repository = repository

    async def create_member_role(
        self, member_role_entity: MemberRoleEntity
    ) -> MemberRoleEntity:
        """
        Creates a new member role.
        """
        try:
            existing_member_role = await self.repository.get_by(
                member_id=member_role_entity.member_id,
                role_id=member_role_entity.role_id,
            )
            if existing_member_role:
                raise ConflictError(
                    error="Member role already exists for this member and role combination"
                )

            new_member_role = await self.repository.add(member_role_entity)
            if not new_member_role or not new_member_role.id:
                raise ServerError(error="Failed to create member role")
            new_member_role.add_event(
                MemberRoleCreatedEvent(
                    member_role_id=new_member_role.id,
                    member_id=new_member_role.member_id,
                    role_id=new_member_role.role_id,
                )
            )
            return new_member_role
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to create member role", internal_details=str(e)
            ) from e
