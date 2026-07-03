from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel
from src.shared.infrastructure.model.soft_delete_mixin_model import SoftDeleteMixinModel


class OrganizationModel(BaseModel, AuditMixinModel, SoftDeleteMixinModel):
    """
    SQLAlchemy model representing an organization.
    """

    __tablename__ = "org_organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", index=True
    )
    logo: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("sys_auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
