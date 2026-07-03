from dataclasses import dataclass, field

from src.modules.motivation.domain.enums.motivation_enums import (
    QuotesStatusEnum,
    QuotesTextStyleEnum,
)
from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin
from src.shared.domain.mixin.soft_delete_mixin import SoftDeleteMixin
from src.shared.domain.mixin.tenant_mixin import TenantMixin


@dataclass(kw_only=True)
class MotivationQuoteEntity(BaseEntity, AuditMixin, SoftDeleteMixin, TenantMixin):
    """
    Entity representing a motivation quote.
    This table stores both system default quotes and custom organization quotes.
    """

    context: str | None = field(
        default=None,
        metadata={"description": "Motivation quote text"},
    )

    author_name: str | None = field(
        default=None,
        metadata={"description": "Quote author name"},
    )

    is_sys_default: bool = field(
        default=False,
        metadata={
            "description": "True if system default quote, False if custom quote",
            "index": True,
        },
    )

    status: str | None = field(
        default=QuotesStatusEnum.ACTIVE.value,
        metadata={
            "description": "Quote status: active, inactive, draft is managed by FE",
        },
    )

    font_style: str | None = field(
        default=QuotesTextStyleEnum.TIMES_NEW_ROMAN.value,
        metadata={"description": "Quote text style"},
    )

    theme_color: str | None = field(
        default=None,
        metadata={
            "description": "Quote card theme colors in HEX format for each motivation",
        },
    )

    bg_image: str | None = field(
        default=None,
        metadata={"description": "Quote background image"},
    )
