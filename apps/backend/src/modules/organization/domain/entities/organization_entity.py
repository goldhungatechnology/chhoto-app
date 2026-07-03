from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin
from src.shared.domain.mixin.soft_delete_mixin import SoftDeleteMixin


@dataclass(kw_only=True)
class OrganizationEntity(BaseEntity, AuditMixin, SoftDeleteMixin):
    """
    Entity representing an organization.
    """

    name: str = field(metadata={"description": "Organization name"})
    type: str = field(metadata={"description": "Organization type"})
    slug: str = field(
        metadata={"description": "Public slug", "unique": True, "index": True}
    )
    domain: str = field(metadata={"description": "Organization domain", "unique": True})
    owner_id: int = field(
        metadata={
            "description": "Owner user id",
            "index": True,
            "on_delete": "restrict",
        }
    )
    status: str = field(
        metadata={
            "description": "Organization status (e.g., 'active', 'inactive')",
            "index": True,
        },
        default="pending",
    )

    ## Optional fields

    description: str | None = field(default=None)
    logo: str | None = field(default=None)
