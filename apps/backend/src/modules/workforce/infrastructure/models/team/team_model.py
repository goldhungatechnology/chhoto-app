from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel
from src.shared.infrastructure.model.soft_delete_mixin_model import SoftDeleteMixinModel


class TeamModel(BaseModel, AuditMixinModel, SoftDeleteMixinModel):
    """
    SQLAlchemy model representing the Team entity in the database.
    """

    __tablename__ = "org_teams"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    color: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    timezone: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    is_default: Mapped[bool] = mapped_column(nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(255), nullable=False, default="active")
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="cascade"),
        index=True,
        nullable=False,
    )
