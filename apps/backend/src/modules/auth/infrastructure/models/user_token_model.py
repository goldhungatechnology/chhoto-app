from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class UserTokenModel(BaseModel, AuditMixinModel):
    """
    sqlalchemy model representing the User Token entity in the database.

    """

    __tablename__ = "sys_auth_user_tokens"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("sys_auth_users.id", ondelete="cascade"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    ## Optional fields
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
