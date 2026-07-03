from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel


class UserAccountModel(BaseModel):
    """
    sqlalchemy model representing the User Account entity in the database.
    """

    __tablename__ = "sys_auth_user_accounts"

    type: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("sys_auth_users.id", ondelete="cascade"), nullable=False, index=True
    )

    ## Optional fields
    hashed_password: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    provider: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    last_password_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
