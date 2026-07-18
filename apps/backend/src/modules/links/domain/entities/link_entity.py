from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.shared.domain.entity.base_entity import BaseEntity


@dataclass(kw_only=True)
class LinkEntity(BaseEntity):
    """
    Link entity
    """

    user_id: int = field(
        metadata={"description": "The ID of the user who owns this link", "index": True}
    )
    destination_url: str = field(
        metadata={"description": "The destination URL the short link redirects to"}
    )
    short_url: str = field(
        metadata={
            "description": "The unique short URL slug",
            "index": True,
            "unique": True,
        }
    )
    tags: list[str] | None = field(
        default=None,
        metadata={"description": "Array of tags for categorizing the link"},
    )
    auto_expire: datetime | None = field(
        default=None,
        metadata={
            "description": "When the link automatically expires, null means never"
        },
    )
    total_clicks: int = field(
        default=0,
        metadata={"description": "Total number of times this link has been clicked"},
    )
    title: str | None = field(
        default=None, metadata={"description": "Optional title for the link"}
    )

    def increment_clicks(self):
        """
        Increment the total clicks for this link by 1
        """
        self.total_clicks += 1
        self.mark_updated()

    def is_expired(self) -> bool:
        """
        Check if the link is expired based on the auto_expire field
        """
        if self.auto_expire is None:
            return False
        return datetime.now(UTC) >= self.auto_expire
