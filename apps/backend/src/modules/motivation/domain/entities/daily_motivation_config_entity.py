from dataclasses import dataclass, field

from src.modules.motivation.domain.enums.motivation_enums import QuotesTextStyleEnum
from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin
from src.shared.domain.mixin.tenant_mixin import TenantMixin


@dataclass(kw_only=True)
class DailyMotivationConfigEntity(BaseEntity, AuditMixin, TenantMixin):
    """
    Entity representing organization-level motivation configuration.
    """

    sys_quote_source: bool | None = field(
        default=True,
        metadata={
            "description": "Whether system/global quotes are used as fallback/source",
            "index": True,
        },
    )

    is_enabled: bool | None = field(
        default=True,
        metadata={
            "description": "Whether daily motivational quotes are enabled",
            "index": True,
        },
    )

    allow_reactions: bool | None = field(
        default=True,
        metadata={"description": "Whether reactions are allowed on quotes"},
    )

    display_time: str | None = field(
        default="09:00 AM",
        metadata={
            "description": "Time to display the daily motivation quote (HH:MM format)",
        },
    )

    font_style: str | None = field(
        default=QuotesTextStyleEnum.TIMES_NEW_ROMAN.value,
        metadata={"description": "Font style for the daily motivation quote"},
    )
