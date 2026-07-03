from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from src.core.config.settings import config
from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


@dataclass(kw_only=True)
class UserSessionEntity(BaseEntity, AuditMixin):
    """
    Entity representing user session in the system.
    """

    user_id: int = field(
        metadata={
            "description": "The ID of the user associated with this session",
            "index": True,
            "on_delete": "cascade",
        }
    )

    expires_at: datetime = field(
        metadata={"description": "The datetime when the session expires"}
    )

    ## Optional fields
    device: str | None = field(
        default=None,
        metadata={
            "description": "Information about the device used for the session (e.g., 'iPhone 12, iOS 14')"
        },
    )
    ip_address: str | None = field(
        default=None,
        metadata={"description": "The IP address from which the session was initiated"},
    )
    browser: str | None = field(
        default=None,
        metadata={
            "description": "The browser used for the session (e.g., 'Chrome 90')"
        },
    )
    revoked_at: datetime | None = field(
        default=None,
        metadata={
            "description": "The datetime when the session was revoked, if applicable"
        },
    )


    @staticmethod
    def set_expiration() -> datetime:
        """
        Generates an expiration datetime for the session based on the current time and the specified number of hours.
        By default, sessions expire after 24 hours.
        """
        return datetime.now(UTC) + timedelta(minutes=config.USER_SESSION_EXPIRE_MINUTES)

    def is_expired(self) -> bool:
        """
        Checks if the session has expired based on the current time and the expires_at field.
        """
        return datetime.now(UTC) >= self.expires_at

    def is_revoked(self) -> bool:
        """
        Checks if the session is revoked
        """
        return self.revoked_at is not None

    def revoke(self):
        """
        Revokes the session by setting the revoked_at field to the current datetime.
        """
        self.revoked_at = datetime.now(UTC)
