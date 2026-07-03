from sqlalchemy import Boolean, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel
from src.shared.infrastructure.model.tenant_mixin_model import TenantMixinModel


class VisitorModel(BaseModel, TenantMixinModel):
    """
    SQLAlchemy model representing a website visitor scoped to an organization.
    """

    __tablename__ = "org_visitors"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "external_id", name="uq_org_visitor_external_id"
        ),
    )

    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    last_seen_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    visit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_identified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)
