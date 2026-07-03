from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class UserMFAModel(BaseModel, AuditMixinModel):
    """
    sqlalchemy model representing the User MFA entity in the database.
    """

    __tablename__ = "sys_auth_user_mfas"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("sys_auth_users.id", ondelete="cascade"), nullable=False, index=True
    )
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str] = mapped_column(String(255), nullable=False)

    ##Optional fields
    auth_url: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
