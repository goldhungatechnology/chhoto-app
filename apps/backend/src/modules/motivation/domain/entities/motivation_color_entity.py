from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


@dataclass(kw_only=True)
class MotivationColorEntity(BaseEntity, AuditMixin):
    """
    Entity representing motivation color theme.

    Colors belong to a motivation config.
    The queue order is based on created_at ASC and id ASC.
    """

    config_id: int = field(
        metadata={
            "description": "Motivation config id",
            "index": True,
        }
    )

    color_code: str = field(
        metadata={
            "description": "Color code selected by admin",
        }
    )
