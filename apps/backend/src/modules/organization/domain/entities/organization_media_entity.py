from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


@dataclass(kw_only=True)
class OrganizationMediaEntity(BaseEntity, AuditMixin):
    """
    Entity representing organization media/contact details.
    """

    organization_id: int = field(
        metadata={
            "description": "Organization id",
            "index": True,
            "unique": True,
            "on_delete": "cascade",
        }
    )

    whatsapp: str | None = field(
        default=None,
        metadata={
            "description": "Organization WhatsApp number",
        },
    )

    linkedin: str | None = field(
        default=None,
        metadata={
            "description": "Organization LinkedIn profile URL",
        },
    )

    email: str | None = field(
        default=None,
        metadata={
            "description": "Organization email address",
        },
    )

    phone_number: str | None = field(
        default=None,
        metadata={
            "description": "Organization phone number",
        },
    )

    messenger: str | None = field(
        default=None,
        metadata={
            "description": "Organization Messenger username",
        },
    )

    instagram: str | None = field(
        default=None,
        metadata={
            "description": "Organization Instagram profile URL",
        },
    )

    twitter: str | None = field(
        default=None,
        metadata={
            "description": "Organization Twitter profile URL",
        },
    )

    telegram: str | None = field(
        default=None,
        metadata={
            "description": "Organization Telegram username",
        },
    )
