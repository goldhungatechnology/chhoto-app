from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel


class LinkSessionModel(BaseModel):
    """
    SQLAlchemy model representing the sys_link_sessions table.
    """

    __tablename__ = "sys_link_sessions"

    link_id: Mapped[int] = mapped_column(
        ForeignKey("sys_links.id", ondelete="cascade"),
        nullable=False,
        index=True,
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    device: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    browser: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    referral_source: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )

    def __str__(self) -> str:
        return f"LinkSessionModel(id={self.id}, link_id={self.link_id})"

    def __repr__(self) -> str:
        return self.__str__()
