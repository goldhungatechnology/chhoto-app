from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.db import Base


class TenantMixinModel(Base):
    """
    Mixin class to add tenant (organization) isolation to models.
    """

    __abstract__ = True

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
