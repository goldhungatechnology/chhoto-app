from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel
from src.shared.infrastructure.model.soft_delete_mixin_model import SoftDeleteMixinModel


class RoleModel(BaseModel, AuditMixinModel, SoftDeleteMixinModel):
    """
    sqlalchemy model representing the Role entity in the database.
    """

    __tablename__ = "org_roles"
    __table_args__ = (
        UniqueConstraint("name", "organization_id", name="uq_org_roles_name_org"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    is_system_role: Mapped[bool] = mapped_column(nullable=False, default=False)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="cascade"),
        index=True,
        nullable=False,
    )
