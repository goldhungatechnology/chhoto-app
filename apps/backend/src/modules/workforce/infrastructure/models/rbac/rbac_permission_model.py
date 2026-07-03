from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class PermissionModel(BaseModel, AuditMixinModel):
    """
    SQLAlchemy model representing a permission in the RBAC system.
    """

    __tablename__ = "org_permissions"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    category: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    is_system_permission: Mapped[bool] = mapped_column(nullable=False, default=False)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
