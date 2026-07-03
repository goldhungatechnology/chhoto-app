from abc import abstractmethod
from src.modules.workforce.domain.entities.rbac.rbac_permission_entity import (
    PermissionEntity,
)
from src.shared.domain.repository.organization_repository_interface import (
    IOrganizationRepository,
)


class IPermissionRepository(IOrganizationRepository[PermissionEntity]):
    """
    Repository interface for managing Permission instances in the RBAC system.
    """

    @abstractmethod
    async def list_permissions_by_organization_id(self) -> list[PermissionEntity]:
        """
        Lists all permissions for the organization.
        """
        pass
