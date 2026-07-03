from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel


class BillingSubscriptionModel(BaseModel):
    """
    SQLAlchemy model representing an organization's billing subscription.
    """

    __tablename__ = "sys_subscriptions"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("sys_plans.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(55), nullable=False)

    auto_renew: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    start_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    billing_cycle: Mapped[str] = mapped_column(String(55), nullable=False)

    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
