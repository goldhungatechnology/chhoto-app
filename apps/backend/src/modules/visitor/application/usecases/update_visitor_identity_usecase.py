from dataclasses import replace
from datetime import UTC, datetime

from src.modules.visitor.domain.constants import (
    EVENT_SESSION_STARTED,
    PRESENCE_TTL_SECONDS,
)
from src.modules.visitor.domain.ports.visitor_presence_notifier import (
    IVisitorPresenceNotifier,
)
from src.modules.visitor.domain.ports.visitor_presence_store import (
    IVisitorPresenceStore,
)
from src.modules.visitor.domain.repositories.visitor_repository import (
    IVisitorRepository,
)
from src.modules.visitor.presentation.schemas.visitor_schemas import (
    UpdateSessionRequestSchema,
)
from src.shared.exceptions.base_exceptions import (
    NotFoundError,
    ServerError,
)


class UpdateVisitorIdentityUseCase:
    """
    Updates the visitor's identity information (name, email) mid-session.
    Persists updates to database, refreshes Redis presence cache, and broadcasts
    the updated session snapshot to organization agents.
    """

    def __init__(
        self,
        visitor_repository: IVisitorRepository,
        presence_store: IVisitorPresenceStore,
        presence_notifier: IVisitorPresenceNotifier,
    ):
        self.visitor_repository = visitor_repository
        self.presence_store = presence_store
        self.presence_notifier = presence_notifier

    async def execute(self, payload: UpdateSessionRequestSchema) -> dict:
        try:
            # 1. Fetch visitor from database by uuid
            visitor = await self.visitor_repository.get_by_uuid(payload.visitor_uuid)
            if not visitor:
                raise NotFoundError(
                    error=f"Visitor not found with uuid {payload.visitor_uuid}"
                )

            # 2. Update identity fields in database
            visitor.identify(
                name=payload.name, email=payload.email, phone=payload.phone
            )
            await self.visitor_repository.update(visitor)

            if visitor.organization_id is None or visitor.id is None:
                raise ValueError("Visitor record is incomplete")

            # 3. If there is an active session/presence in Redis cache, update it
            session_uuid = None
            try:
                presence = await self.presence_store.get_presence(
                    organization_id=visitor.organization_id,
                    visitor_id=visitor.id,
                )
                if presence:
                    # Update presence fields using dataclasses.replace
                    updated_presence = replace(
                        presence,
                        name=visitor.name,
                        email=visitor.email,
                        phone=visitor.phone,
                        is_identified=visitor.is_identified,
                        status="active",
                        last_seen=datetime.now(UTC).isoformat(),
                    )
                    session_uuid = updated_presence.session_uuid

                    # Write updated presence back to cache
                    await self.presence_store.set_presence(
                        updated_presence, PRESENCE_TTL_SECONDS
                    )

                    # Notify dashboard agents of updated identity
                    await self.presence_notifier.notify(
                        visitor.organization_id,
                        {
                            "type": EVENT_SESSION_STARTED,
                            "visitor": updated_presence.to_dict(),
                        },
                    )
            except Exception as error:
                # Log and ignore cache update errors to prevent DB rollback
                print(f"Failed to update active visitor presence cache: {error}")

            return {
                "visitor_uuid": visitor.uuid,
                "session_uuid": session_uuid,
                "name": visitor.name,
                "email": visitor.email,
                "phone": visitor.phone,
                "is_identified": visitor.is_identified,
            }

        except NotFoundError:
            raise
        except Exception as error:
            raise ServerError(
                error="Failed to update visitor identity", internal_details=str(error)
            ) from error
