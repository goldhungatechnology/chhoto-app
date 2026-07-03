from abc import ABC, abstractmethod

from src.modules.visitor.domain.value_objects.visitor_presence import VisitorPresence


class IVisitorPresenceStore(ABC):
    """
    Port for the real-time presence store (implemented over Redis). Presence is
    ephemeral state with a short TTL; the relational tables remain the source of
    truth for history.
    """

    @abstractmethod
    async def get_presence(
        self, *, organization_id: int, visitor_id: int
    ) -> VisitorPresence | None:
        """Retrieve a visitor's presence snapshot."""

    @abstractmethod
    async def set_presence(self, presence: VisitorPresence, ttl: int) -> None:
        """Store/replace a visitor's presence snapshot and (re)set its TTL."""

    @abstractmethod
    async def touch(
        self, *, organization_id: int, visitor_id: int, last_seen: str, ttl: int
    ) -> bool:
        """
        Refresh the last-seen timestamp and TTL of an existing presence record.
        Returns ``True`` when a record existed and was refreshed, ``False`` when
        the presence had already expired.
        """

    @abstractmethod
    async def delete_presence(self, *, organization_id: int, visitor_id: int) -> None:
        """Remove a visitor's presence snapshot."""

    @abstractmethod
    async def list_active(self, organization_id: int) -> list[VisitorPresence]:
        """List all live presence snapshots for an organization."""

    @abstractmethod
    async def set_session_index(
        self, *, session_uuid: str, organization_id: int, visitor_id: int, ttl: int
    ) -> None:
        """
        Maintain a ``session_uuid -> (organization_id, visitor_id)`` lookup so a
        heartbeat/end carrying only a ``session_uuid`` can locate its presence.
        """

    @abstractmethod
    async def get_session_index(self, session_uuid: str) -> tuple[int, int] | None:
        """Resolve a ``session_uuid`` to ``(organization_id, visitor_id)``."""

    @abstractmethod
    async def delete_session_index(self, session_uuid: str) -> None:
        """Remove the session lookup entry."""
