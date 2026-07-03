from datetime import UTC, datetime
from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity


@dataclass(kw_only=True)
class UserAccountEntity(BaseEntity):
    """
    Entity representing user account in the system.
    """

    type: str = field(
        metadata={
            "description": "The type of the user account (e.g., 'credentials', 'oauth')"
        }
    )
    user_id: int = field(
        metadata={
            "description": "The ID of the user associated with this account",
            "index": True,
            "on_delete": "cascade",
        }
    )

    ## Optional fields
    hashed_password: str | None = field(
        default=None,
        metadata={
            "description": "The hashed password for the user account, required if type is 'credentials'"
        },
    )
    provider: str | None = field(
        default=None,
        metadata={
            "description": "The OAuth provider for the user account, required if type is 'oauth'"
        },
    )
    last_password_updated_at: datetime | None = field(
        default=None,
        metadata={"description": "The timestamp of the last password update"},
    )

    ## Methods
    def is_credentials(self) -> bool:
        """
        Check if the account type is 'credentials'.
        """
        return self.type == "credentials"

    def is_oauth(self) -> bool:
        """
        Check if the account type is 'oauth'.
        """
        return self.type == "oauth"

    def change_password(self, new_hashed_password: str):
        """
        Change the hashed password for the account.
        """
        if not self.is_credentials():
            raise ValueError("Password can only be changed for 'credentials' accounts")
        self.hashed_password = new_hashed_password
        self.last_password_updated_at = datetime.now(UTC)
