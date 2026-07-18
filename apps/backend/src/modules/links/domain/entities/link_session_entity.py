from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity


@dataclass(kw_only=True)
class LinkSessionEntity(BaseEntity):
    """
    Link session entity
    """

    link_id: int = field(
        metadata={
            "description": "The ID of the link this session belongs to",
            "index": True,
        }
    )
    ip_address: str | None = field(
        default=None, metadata={"description": "The IP address of the visitor"}
    )
    device: str | None = field(
        default=None, metadata={"description": "The device type used by the visitor"}
    )
    browser: str | None = field(
        default=None, metadata={"description": "The browser used by the visitor"}
    )
    referral_source: str | None = field(
        default=None, metadata={"description": "The referral source of the visitor"}
    )
