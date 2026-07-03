from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class MemberRoleModel(BaseModel, AuditMixinModel):
    """
    SQLAlchemy model representing the association between members and roles in the RBAC system.
    """

    __tablename__ = "org_member_roles"

    member_id: Mapped[int] = mapped_column(
        ForeignKey("org_organization_members.id", ondelete="cascade"),
        index=True,
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("org_roles.id", ondelete="cascade"), index=True, nullable=False
    )
