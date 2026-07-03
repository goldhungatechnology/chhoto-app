from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class OrganizationMediaModel(BaseModel, AuditMixinModel):
    """
    SQLAlchemy model representing organization media/contact details.
    """

    __tablename__ = "org_organization_media"
    __table_args__ = (
        UniqueConstraint("organization_id", name="uq_org_organization_media"),
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    whatsapp: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default=None,
    )

    linkedin: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default=None,
    )

    messenger: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )

    instagram: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )

    twitter: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )

    telegram: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )
