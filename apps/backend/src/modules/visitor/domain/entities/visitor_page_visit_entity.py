from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.shared.domain.entity.base_entity import BaseEntity


@dataclass(kw_only=True)
class VisitorPageVisitEntity(BaseEntity):
    """
    Entity representing a single page view within a visitor session. A page visit
    is "open" while ``left_at`` is ``None``; closing it stamps the exit time and
    computes the dwell duration in seconds.
    """

    organization_id: int = field(
        metadata={"description": "Owning organization id", "index": True}
    )
    session_id: int = field(
        metadata={"description": "Owning session id", "index": True}
    )
    visitor_id: int = field(
        metadata={"description": "Owning visitor id", "index": True}
    )

    url: str = field(metadata={"description": "Page URL"})
    page_title: str | None = field(default=None)

    entered_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        metadata={"description": "When the visitor entered the page"},
    )
    left_at: datetime | None = field(default=None)
    duration_seconds: int | None = field(default=None)

    def is_open(self) -> bool:
        """Whether the page visit is still open (visitor has not left)."""
        return self.left_at is None

    def close(self, when: datetime | None = None) -> None:
        """
        Close the page visit, stamping the exit time and computing dwell
        duration. Idempotent: closing an already-closed visit is a no-op.
        """
        if not self.is_open():
            return
        exited = when or datetime.now(UTC)
        self.left_at = exited
        delta = (exited - self.entered_at).total_seconds()
        self.duration_seconds = max(0, int(delta))
        self.mark_updated()
