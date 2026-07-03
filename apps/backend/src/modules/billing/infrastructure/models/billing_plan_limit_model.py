from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel


class BillingPlanLimitModel(BaseModel):
    """
    SQLAlchemy model representing billing plan limits.
    """

    __tablename__ = "sys_plan_limits"
    __table_args__ = (
        UniqueConstraint("plan_id", "feature_key", name="uq_plan_feature_limit"),
    )

    plan_id: Mapped[int] = mapped_column(
        ForeignKey("sys_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    feature_key: Mapped[str] = mapped_column(String(255), nullable=False)
    limit_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_unlimited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
