from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


@dataclass(kw_only=True)
class MemberRoleEntity(BaseEntity, AuditMixin):
    """
    Entity representing the association between a member and a role in the RBAC system.
    """

    member_id: int = field(
        metadata={
            "description": "The ID of the member (organization member) associated with the role",
            "index": True,
            "on_delete": "cascade",
        }
    )
    role_id: int = field(
        metadata={
            "description": "The ID of the role assigned to the member",
            "index": True,
            "on_delete": "cascade",
        }
    )
