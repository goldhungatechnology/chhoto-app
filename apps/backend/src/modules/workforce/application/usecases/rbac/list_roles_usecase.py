from src.modules.auth.domain.ports.user.user_reader import UserReader
from src.modules.workforce.domain.services.rbac.rbac_role_domain_service import (
    RbacRoleDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ListRolesUseCase:
    """
    Use case for listing all roles in the system.
    """

    def __init__(
        self, rbac_role_domain_service: RbacRoleDomainService, user_reader: UserReader
    ):
        self.rbac_role_domain_service = rbac_role_domain_service
        self.user_reader = user_reader

    async def execute(self):
        """
        Executes the use case to list all roles.
        """
        try:
            roles = await self.rbac_role_domain_service.list_roles_by_organization_id()

            user_ids = [
                role.created_by_id for role in roles if role.created_by_id is not None
            ]

            users = await self.user_reader.get_users_by_ids(user_ids)

            users_map = {user.id: user for user in users}

            return roles, users_map
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to list roles", internal_details=str(e)
            ) from e
