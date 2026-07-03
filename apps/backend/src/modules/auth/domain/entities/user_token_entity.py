from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


@dataclass(kw_only=True)
class UserTokenEntity(BaseEntity, AuditMixin):
    """
    Entity representing a usertoken in the system.
    """

    user_id: int = field(
        metadata={
            "index": True,
            "on_delete": "cascade",
            "description": "The ID of the user associated with this token",
        }
    )
    type: str = field(
        metadata={
            "index": True,
            "description": "The type of the token (e.g., 'password_reset', 'email_verification')",
        }
    )
    token_hash: str = field(
        metadata={
            "index": True,
            "description": "The hashed value of the token for secure storage and comparison",
        }
    )
    expires_at: datetime = field(metadata={"index": True})

    ## Optional fields
    used_at: datetime | None = field(
        default=None,
        metadata={"description": "The datetime when the token was used, if applicable"},
    )

    def mark_as_used(self):
        """
        Marks the token as used by setting the used_at timestamp to the current time.
        """
        self.used_at = datetime.now(UTC)
