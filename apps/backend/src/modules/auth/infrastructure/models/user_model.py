from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel
from src.shared.infrastructure.model.soft_delete_mixin_model import SoftDeleteMixinModel


class UserModel(BaseModel, AuditMixinModel, SoftDeleteMixinModel):
    """
    sqlalchemy model representing the User entity in the database.
    """

    __tablename__ = "sys_auth_users"

    username: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    avatar_bg: Mapped[str] = mapped_column(String(255), nullable=False)
    is_onboarded: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[str] = mapped_column(String(255), nullable=False, default="active")

    ## Optional fields
    full_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    phone_number: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    country_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sys_countries.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        default=None,
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    def __str__(self) -> str:
        """Return string representation."""
        return f"UserModel(id={self.id}, full_name='{self.full_name}', email='{self.email}')"

    def __repr__(self) -> str:
        """Return string representation."""
        return self.__str__()
