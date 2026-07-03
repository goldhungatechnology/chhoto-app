from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class UserSessionModel(BaseModel, AuditMixinModel):
    """
    sqlalchemy model representing the User entity in the database.

    Organization uuid is only for support and presever organization context for better ux so it is not a relationship
    rather a string
    """

    __tablename__ = "sys_auth_user_sessions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("sys_auth_users.id", ondelete="cascade"), nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    ## Optional fields
    device: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    ip_address: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    browser: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    organization_uuid: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
