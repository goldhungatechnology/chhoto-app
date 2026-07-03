from src.modules.workforce.domain.entities.rbac.rbac_role_entity import RoleEntity
from src.shared.domain.repository.organization_repository_interface import (
    IOrganizationRepository,
)


class IRoleRepository(IOrganizationRepository[RoleEntity]):
    """
    Repository interface for managing RoleEntity instances in the RBAC system.
    """
