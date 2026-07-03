from dataclasses import dataclass, field
from datetime import datetime

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


@dataclass(kw_only=True)
class UserMFAEntity(BaseEntity, AuditMixin):
    """
    Entity representing a user MFA in the system.
    """

    user_id: int = field(
        metadata={
            "description": "The ID of the user associated with this MFA",
            "index": True,
            "on_delete": "cascade",
        },
    )
    secret: str = field(
        metadata={
            "description": "The secret key for the MFA",
        },
    )
    method: str = field(
        metadata={
            "description": "The method of MFA (e.g., TOTP, SMS, Email)",
        },
    )

    ## Optional fields
    auth_url: str | None = field(
        default=None,
        metadata={
            "description": "The authentication URL for TOTP MFA",
        },
    )

    verified_at: datetime | None = field(
        default=None,
        metadata={
            "description": "The datetime when the MFA was verified",
        },
    )

    revoked_at: datetime | None = field(
        default=None,
        metadata={
            "description": "The datetime when the MFA was revoked",
        },
    )
