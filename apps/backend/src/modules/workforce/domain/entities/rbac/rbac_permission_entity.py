from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


@dataclass(kw_only=True)
class PermissionEntity(BaseEntity, AuditMixin):
    """
    Entity representing a permission in the RBAC system.
    """

    name: str = field(
        metadata={
            "description": "The name of the permission",
            "unique": True,
        }
    )
    key: str = field(
        metadata={
            "description": "A unique key identifier for the permission, used for programmatic access, generated from the name (e.g., 'view_reports' for 'View Reports')",
        }
    )
    description: str | None = field(
        default=None,
        metadata={
            "description": "A brief description of the permission's purpose and scope"
        },
    )
    category: str = field(
        metadata={
            "description": "The category of the permission, used for grouping related permissions (e.g., 'reporting', 'user_management')",
            "index": True,
        }
    )
    is_system_permission: bool = field(
        default=False,
        metadata={
            "description": "Indicates if the permission is a system permission that cannot be modified or deleted"
        },
    )
    organization_id: int | None = field(
        default=None,
        metadata={
            "description": "The ID of the organization this permission belongs to",
            "index": True,
            "on_delete": "cascade",
        },
    )
