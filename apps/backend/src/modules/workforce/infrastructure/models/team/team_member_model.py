from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class TeamMemberModel(BaseModel, AuditMixinModel):
    """
    SQLAlchemy model representing the association between teams and members.
    """

    __tablename__ = "org_team_members"

    team_id: Mapped[int] = mapped_column(
        ForeignKey("org_teams.id", ondelete="cascade"),
        index=True,
        nullable=False,
    )
    member_id: Mapped[int] = mapped_column(
        ForeignKey("org_organization_members.id", ondelete="cascade"),
        index=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(255), nullable=False, default="member")
