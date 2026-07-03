from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.db import Base


class SoftDeleteMixinModel(Base):
    """
    Mixin class to add soft delete functionality to models.
    """

    __abstract__ = True

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
