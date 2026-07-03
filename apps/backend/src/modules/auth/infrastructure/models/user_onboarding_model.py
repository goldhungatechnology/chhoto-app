from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class UserOnboardingModel(BaseModel, AuditMixinModel):
    """
    sqlalchemy model representing the User entity in the database.
    """

    __tablename__ = "sys_auth_user_onboardings"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("sys_auth_users.id", ondelete="cascade"), nullable=False, index=True
    )
    theme: Mapped[str] = mapped_column(String(255), nullable=False, default="light")
    referral_source: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
