from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin
from src.shared.domain.mixin.soft_delete_mixin import SoftDeleteMixin


@dataclass(kw_only=True)
class RoleEntity(BaseEntity, AuditMixin, SoftDeleteMixin):
    """
    Entity representing a role in the RBAC system.
    """

    name: str = field(
        metadata={
            "description": "The name of the role",
        }
    )
    description: str | None = field(
        default=None,
        metadata={
            "description": "A brief description of the role's purpose and permissions"
        },
    )

    is_system_role: bool = field(
        default=False,
        metadata={
            "description": "Indicates if the role is a system role that cannot be modified or deleted"
        },
    )

    organization_id: int = field(
        metadata={
            "description": "The ID of the organization this role belongs to",
            "index": True,
            "on_delete": "cascade",
        }
    )

    ## Methods

    def is_active(self) -> bool:
        """
        Check if the role is active (not soft-deleted).
        """
        return self.deleted_at is None
