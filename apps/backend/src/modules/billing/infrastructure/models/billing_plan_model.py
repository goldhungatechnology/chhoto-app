from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel


class BillingPlanModel(BaseModel):
    """
    SQLAlchemy model representing a billing plan.
    """

    __tablename__ = "sys_plans"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    interval: Mapped[str] = mapped_column(String(55), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
