from src.modules.workforce.domain.entities.rbac.rbac_permission_entity import (
    PermissionEntity,
)
from src.modules.workforce.domain.repositories.rbac.rbac_permission_repository import (
    IPermissionRepository,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class RbacPermissionDomainService:
    """
    service class for RBAC Permission domain logic
    """

    def __init__(self, repository: IPermissionRepository):
        self.repository = repository

    async def list_permissions_by_organization_id(self) -> list[PermissionEntity]:
        """
        Lists all permissions
        """
        try:
            return await self.repository.list_permissions_by_organization_id()

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to list permissions", internal_details=str(e)
            ) from e
