from datetime import datetime

from sqlalchemy import DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel


class OutboxModel(BaseModel):
    """
    outbox model
    """

    __tablename__ = "sys_outbox_events"

    event_type: Mapped[str] = mapped_column(nullable=False, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    processed: Mapped[bool] = mapped_column(default=False, index=True)
    retry_count: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[str | None]
    locked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
