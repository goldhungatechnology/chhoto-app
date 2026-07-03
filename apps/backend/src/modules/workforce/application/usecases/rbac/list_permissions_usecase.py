from src.modules.auth.domain.ports.user.user_reader import UserReader
from src.modules.workforce.domain.services.rbac.rbac_permission_domain_service import (
    RbacPermissionDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ListPermissionsUseCase:
    """
    Use case for listing all permissions in the system.
    """

    def __init__(
        self,
        rbac_permission_domain_service: RbacPermissionDomainService,
        user_reader: UserReader,
    ):
        self.rbac_permission_domain_service = rbac_permission_domain_service
        self.user_reader = user_reader

    async def execute(self):
        """
        Executes the use case to list all permissions.
        """
        try:
            permissions = await self.rbac_permission_domain_service.list_permissions_by_organization_id()

            user_ids = [
                permission.created_by_id
                for permission in permissions
                if permission.created_by_id is not None
            ]

            users = await self.user_reader.get_users_by_ids(user_ids)
            users_map = {user.id: user for user in users}

            return permissions, users_map
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to list permissions", internal_details=str(e)
            ) from e
