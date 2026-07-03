from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class InvitationModel(BaseModel, AuditMixinModel):
    """
    SQLAlchemy model for org_invitations.
    """

    __tablename__ = "org_invitations"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="cascade"),
        index=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("org_roles.id", ondelete="restrict"), nullable=False
    )
    team_id: Mapped[int | None] = mapped_column(
        ForeignKey("org_teams.id", ondelete="set null"), nullable=True, default=None
    )
    invited_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("sys_auth_users.id", ondelete="set null"), nullable=True
    )
    hashed_token: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending", index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
