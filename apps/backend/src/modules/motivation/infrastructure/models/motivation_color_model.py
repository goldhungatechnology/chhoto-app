from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class MotivationColorModel(BaseModel, AuditMixinModel):
    """
    SQLAlchemy model representing motivation color codes.

    Colors belong to a daily motivation config.
    Queue order is determined by created_at ASC and id ASC.
    """

    __tablename__ = "org_motivation_colors"

    config_id: Mapped[int] = mapped_column(
        ForeignKey("org_motivation_configs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    color_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_org_motivation_colors_config_created",
            "config_id",
            "created_at",
        ),
    )
