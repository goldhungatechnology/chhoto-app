from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class OrganizationMemberModel(BaseModel, AuditMixinModel):
    """
    SQLAlchemy model representing organization membership.
    """

    __tablename__ = "org_organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member_user"),
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("sys_auth_users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(255), nullable=False, default="active")
