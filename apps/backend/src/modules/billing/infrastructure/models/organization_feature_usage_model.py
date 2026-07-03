from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel


class OrganizationFeatureUsageModel(BaseModel):
    """
    SQLAlchemy model representing feature usage of an organization subscription.
    """

    __tablename__ = "org_feature_usages"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("sys_subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    feature_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    used_value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
