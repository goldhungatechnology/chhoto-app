from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel


class VisitorPageVisitModel(BaseModel):
    """
    SQLAlchemy model representing a single page view within a visitor session.
    """

    __tablename__ = "org_visitor_page_visits"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[int] = mapped_column(
        ForeignKey("org_visitor_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    visitor_id: Mapped[int] = mapped_column(
        ForeignKey("org_visitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    url: Mapped[str] = mapped_column(Text, nullable=False)
    page_title: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    entered_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    left_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    duration_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None
    )
