from sqlalchemy import Boolean, true
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel
from src.shared.infrastructure.model.tenant_mixin_model import TenantMixinModel


class DailyMotivationConfigModel(BaseModel, TenantMixinModel, AuditMixinModel):
    """
    SQLAlchemy model representing organization-level motivation configuration.
    """

    __tablename__ = "org_motivation_configs"

    sys_quote_source: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
        index=True,
    )

    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
        index=True,
    )

    allow_reactions: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    display_time: Mapped[str] = mapped_column(
        nullable=False,
        default="09:00 AM",
    )

    font_style: Mapped[str] = mapped_column(nullable=False, default="Times New Roman")
