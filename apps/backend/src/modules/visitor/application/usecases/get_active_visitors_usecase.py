from src.modules.visitor.domain.ports.visitor_presence_store import (
    IVisitorPresenceStore,
)
from src.modules.visitor.domain.value_objects.visitor_presence import VisitorPresence


class GetActiveVisitorsUseCase:
    """
    Returns the live presence snapshots for an organization, read exclusively
    from the real-time store (Redis). Used by the agent dashboard.
    """

    def __init__(self, presence_store: IVisitorPresenceStore):
        self.presence_store = presence_store

    async def execute(self, organization_id: int) -> list[VisitorPresence]:
        """List active visitors for the organization."""
        return await self.presence_store.list_active(organization_id)
