from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.tenant_mixin import TenantMixin


@dataclass(kw_only=True)
class VisitorEntity(BaseEntity, TenantMixin):
    """
    Entity representing an anonymous (or identified) website visitor scoped to a
    single organization. A visitor is uniquely identified within an organization
    by its ``external_id`` (the SDK-generated ``visitor_uuid`` stored in the
    browser). The server-generated ``uuid`` (from ``BaseEntity``) is the public
    identifier exposed to agent dashboards.
    """

    external_id: str = field(
        metadata={
            "description": "SDK-generated visitor uuid (unique per organization)",
            "index": True,
        }
    )

    last_seen_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        metadata={"description": "Last time the visitor was seen"},
    )
    visit_count: int = field(
        default=1, metadata={"description": "Number of distinct visits"}
    )
    is_identified: bool = field(
        default=False,
        metadata={"description": "Whether the visitor has been identified"},
    )

    name: str | None = field(default=None)
    email: str | None = field(default=None)
    phone: str | None = field(default=None)

    def register_return_visit(self) -> None:
        """
        Record a brand new visit for a returning visitor: bump the visit counter
        and refresh the last-seen timestamp.
        """
        self.visit_count += 1
        self.touch_last_seen()

    def touch_last_seen(self) -> None:
        """
        Refresh the last-seen timestamp (also marks the entity as updated).
        """
        self.last_seen_at = datetime.now(UTC)
        self.mark_updated()

    def identify(
        self,
        *,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
    ) -> None:
        """
        Attach identity information to the visitor. Any provided field is applied;
        the visitor is flagged as identified once any identity is known.
        """
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        if self.name or self.email or self.phone:
            self.is_identified = True
        self.mark_updated()
