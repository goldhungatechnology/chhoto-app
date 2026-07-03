from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.repository.outbox_repository_interface import IOutboxRepository
from src.shared.infrastructure.outbox.outbox_repository import OutboxRepositoryImpl


class OutboxService:
    """
    outbox service class
    """

    def __init__(self, repository: IOutboxRepository):
        self.repository = repository

    async def add_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """
        add event to the outbox table, this will be called within the same transaction as the main operation, ensuring atomicity.
        """
        await self.repository.add(event_type, payload)


async def get_outbox_service(session: AsyncSession) -> OutboxService:
    """
    get outbox service instance
    """

    repository = OutboxRepositoryImpl(session)
    return OutboxService(repository)
