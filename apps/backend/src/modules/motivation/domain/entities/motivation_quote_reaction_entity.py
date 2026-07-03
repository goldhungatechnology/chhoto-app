from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


@dataclass(kw_only=True)
class MotivationQuoteReactionEntity(BaseEntity, AuditMixin):
    """
    Entity representing a member reaction on a motivation quote.
    """

    organization_id: int = field(
        metadata={
            "description": "Organization id",
            "index": True,
            "on_delete": "cascade",
        }
    )

    member_id: int = field(
        metadata={
            "description": "Organization member id who reacted",
            "index": True,
        }
    )

    quote_id: int = field(
        metadata={
            "description": "Motivation quote id",
            "index": True,
            "on_delete": "cascade",
        }
    )

    reaction_type: str = field(
        metadata={"description": "Reaction type, for example like, heart, clap"},
    )
