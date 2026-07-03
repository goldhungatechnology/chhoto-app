from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.db import Base


class AuditMixinModel(Base):
    """
    Mixin class to add audit fields to models.
    """

    __abstract__ = True

    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("sys_auth_users.id"), nullable=True
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("sys_auth_users.id"), nullable=True
    )
