from datetime import datetime

from sqlalchemy import ARRAY, BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel


class LinkModel(BaseModel):
    """
    SQLAlchemy model representing the sys_links table.
    """

    __tablename__ = "sys_links"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("sys_auth_users.id", ondelete="cascade"),
        nullable=False,
        index=True,
    )
    destination_url: Mapped[str] = mapped_column(Text, nullable=False)
    short_url: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    auto_expire: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_clicks: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)

    def __str__(self) -> str:
        return f"LinkModel(id={self.id}, short_url='{self.short_url}')"

    def __repr__(self) -> str:
        return self.__str__()
