from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel


class AuditLogModel(BaseModel):
    """
    SQLAlchemy model for append-only audit logs.
    """

    __tablename__ = "sys_audit_logs"

    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_table: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    before_data: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    after_data: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("sys_auth_users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    request_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None, index=True
    )
    client_ip: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    client_country: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None
    )
    client_city: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None
    )
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
