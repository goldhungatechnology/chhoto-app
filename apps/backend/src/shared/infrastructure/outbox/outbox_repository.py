import json
import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.repository.outbox_repository_interface import IOutboxRepository
from src.shared.infrastructure.outbox.outbox_models import OutboxModel


class OutboxRepositoryImpl(IOutboxRepository):
    """
    SQLAlchemy implementation of the outbox repository interface.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, event_type: str, payload: dict[str, Any]) -> None:
        """
        Add an event to the outbox table in the current transaction.
        """
        sql = text(
            f"INSERT INTO {OutboxModel.__tablename__}  (uuid,event_type, payload,processed, retry_count) "
            f"VALUES (:uuid,:event_type, :payload, false, 0) "
            f"RETURNING *"
        )

        try:
            await self.session.execute(
                sql,
                {
                    "uuid": str(uuid.uuid4()),
                    "event_type": event_type,
                    "payload": json.dumps(payload),
                },
            )
        except Exception as e:
            raise Exception(f"Failed to add outbox event: {e!s}") from e
