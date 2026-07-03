from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import ClassVar

from src.core.config.settings import config
from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin
from src.shared.domain.mixin.soft_delete_mixin import SoftDeleteMixin


@dataclass(kw_only=True)
class UserEntity(BaseEntity, AuditMixin, SoftDeleteMixin):
    """
    Entity representing a user in the system.
    """

    TEMP_DOMAINS: ClassVar[set[str]] = set(config.TEMP_EMAIL_DOMAINS)

    username: str = field(metadata={"unique": True, "index": True})
    email: str = field(metadata={"unique": True, "index": True})
    avatar_bg: str = field(
        metadata={
            "description": "The background color for the user's avatar, it should be random"
        },
    )
    is_onboarded: bool = field(
        default=False,
        metadata={
            "description": "Whether the user has completed onboarding",
        },
    )
    status: str = field(
        metadata={
            "description": "The status message of the user (Active, Inactive, suspended,banned)"
        },
    )

    ## Optional fields
    full_name: str | None = field(
        default=None, metadata={"description": "The full name of the user"}
    )
    avatar: str | None = field(
        default=None, metadata={"description": "The avatar URL of the user"}
    )
    phone_number: str | None = field(
        default=None, metadata={"description": "The phone number of the user"}
    )
    country_id: int | None = field(
        default=None,
        metadata={
            "description": "The ID of the country the user belongs to",
            "index": True,
        },
    )
    email_verified_at: datetime | None = field(
        default=None,
        metadata={"description": "The datetime when the user's email was verified"},
    )

    ## Methods
    def is_deleted(self) -> bool:
        """
        Check if the user is active (not soft-deleted).
        """
        return self.deleted_at is not None

    def is_active(self) -> bool:
        """
        Check if the user is active (not soft-deleted and not suspended).
        """
        if self.status and self.status.lower() == "active":
            return True
        return False

    def is_email_verified(self) -> bool:
        """
        Check if the user's email is verified.
        """
        return self.email_verified_at is not None

    def mark_email_verified(self):
        """
        Mark the user's email as verified by setting the email_verified_at field to the current datetime.
        """
        self.email_verified_at = datetime.now(UTC)

    def change_full_name(self, full_name: str):
        """
        Change the user's full name and mark the entity as updated.
        """
        self.full_name = full_name
        self.mark_updated()

    def complete_onboarding(self):
        """
        Mark the user as having completed onboarding and mark the entity as updated.
        """
        self.is_onboarded = True
        self.mark_updated()

    def update_status(self, status: str):
        """
        Update the user's status and mark the entity as updated.
        """
        self.status = status
        self.mark_updated()

    def is_temporary_email(self) -> bool:
        """
        Check if the user's email is from a temporary email domain.
        """
        domain = self.email.split("@")[-1].lower()
        return domain in self.TEMP_DOMAINS

    @staticmethod
    def generate_random_avatar_bg() -> str:
        """
        Generate a random background color for the user's avatar.
        """
        import random

        return f"#{random.randint(0, 0xFFFFFF):06x}"

    @staticmethod
    def generate_username(email: str) -> str:
        """
        Generate a username based on the email address.
        """
        import random
        import string

        base = email.split("@")[0].lower()

        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))

        return f"{base}_{suffix}"
