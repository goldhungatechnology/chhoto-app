from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class UserMFARecoveryCodeModel(BaseModel, AuditMixinModel):
    """
    sqlalchemy model representing the User MFA recovery entity in the database.
    """

    __tablename__ = "sys_auth_user_mfa_recovery_codes"

    mfa_id: Mapped[int] = mapped_column(
        ForeignKey("sys_auth_user_mfas.id", ondelete="cascade"),
        nullable=False,
        index=True,
    )
    hashed_recovery_code: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    is_revoked: Mapped[bool] = mapped_column(default=False, nullable=False)
