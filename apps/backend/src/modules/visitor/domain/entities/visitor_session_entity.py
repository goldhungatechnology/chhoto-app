from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.shared.domain.entity.base_entity import BaseEntity

# Allowed lifecycle states for a visitor session.
SESSION_STATUS_ACTIVE = "active"
SESSION_STATUS_INACTIVE = "inactive"
SESSION_STATUS_ENDED = "ended"


@dataclass(kw_only=True)
class VisitorSessionEntity(BaseEntity):
    """
    Entity representing a single browsing session for a visitor. The
    server-generated ``uuid`` is the ``session_uuid`` handed back to the SDK and
    used as the correlation key for every subsequent page / heartbeat / end call.
    """

    organization_id: int = field(
        metadata={"description": "Owning organization id", "index": True}
    )
    visitor_id: int = field(
        metadata={"description": "Owning visitor id", "index": True}
    )

    status: str = field(
        default=SESSION_STATUS_ACTIVE,
        metadata={"description": "Session status: active | inactive | ended"},
    )
    started_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        metadata={"description": "When the session started"},
    )
    ended_at: datetime | None = field(default=None)

    ip_address: str | None = field(default=None)
    user_agent: str | None = field(default=None)
    referer: str | None = field(default=None)
    landing_page: str | None = field(default=None)

    def is_ended(self) -> bool:
        """Whether the session has already been terminated."""
        return self.status == SESSION_STATUS_ENDED

    def mark_inactive(self) -> None:
        """
        Flip an active session to inactive (used by presence sweeps). Ended
        sessions are left untouched.
        """
        if self.status == SESSION_STATUS_ACTIVE:
            self.status = SESSION_STATUS_INACTIVE
            self.mark_updated()

    def reactivate(self) -> None:
        """Flip an inactive session back to active (e.g. heartbeat resumed)."""
        if self.status == SESSION_STATUS_INACTIVE:
            self.status = SESSION_STATUS_ACTIVE
            self.mark_updated()

    def end(self) -> None:
        """
        Terminate the session. Idempotent: ending an already-ended session is a
        no-op.
        """
        if self.is_ended():
            return
        self.status = SESSION_STATUS_ENDED
        self.ended_at = datetime.now(UTC)
        self.mark_updated()
