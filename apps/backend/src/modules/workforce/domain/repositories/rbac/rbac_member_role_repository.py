from src.modules.workforce.domain.entities.rbac.rbac_member_role_entity import (
    MemberRoleEntity,
)
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IMemberRoleRepository(IBaseRepository[MemberRoleEntity]):
    """
    Repository interface for managing MemberRoleEntity instances in the RBAC system.
    """
