from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel


class VisitorSessionModel(BaseModel):
    """
    SQLAlchemy model representing a single visitor browsing session.
    """

    __tablename__ = "org_visitor_sessions"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    visitor_id: Mapped[int] = mapped_column(
        ForeignKey("org_visitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active", index=True
    )
    started_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ended_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(64), nullable=True, default=None
    )
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    referer: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    landing_page: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
