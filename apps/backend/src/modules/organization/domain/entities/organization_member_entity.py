from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


@dataclass(kw_only=True)
class OrganizationMemberEntity(BaseEntity, AuditMixin):
    """
    Entity representing an organization membership.
    """

    organization_id: int = field(
        metadata={
            "description": "Organization id",
            "index": True,
            "on_delete": "cascade",
        }
    )
    user_id: int = field(
        metadata={
            "description": "User id",
            "index": True,
            "on_delete": "cascade",
        }
    )

    status: str = field(default="active")
