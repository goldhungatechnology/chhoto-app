from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel
from src.shared.infrastructure.model.soft_delete_mixin_model import SoftDeleteMixinModel


class MotivationQuoteModel(BaseModel, AuditMixinModel, SoftDeleteMixinModel):
    """
    SQLAlchemy model representing motivation quotes.
    It stores both system default quotes and custom organization quotes.
    Custom organization quotes have organization_id.
    Global system/default quotes have organization_id=None.
    """

    __tablename__ = "org_motivation_quotes"

    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    Context: Mapped[str] = mapped_column(Text, nullable=False)

    author_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )

    is_sys_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        index=True,
    )

    language_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="en",
        index=True,
    )

    display_time: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="09:00 AM",
    )

    text_style: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="bricolage_grotesque",
    )

    theme_color: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="purple",
    )

    bg_image: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        default=None,
    )

    __table_args__ = (
        Index(
            "ix_org_motivation_quotes_org_default", "organization_id", "is_sys_default"
        ),
        Index("ix_org_motivation_quotes_org_status", "organization_id", "status"),
        Index(
            "ix_org_motivation_quotes_org_default_status",
            "organization_id",
            "is_sys_default",
            "status",
        ),
        Index(
            "ix_org_motivation_quotes_org_default_status_deleted",
            "organization_id",
            "is_sys_default",
            "status",
            "deleted_at",
        ),
    )
